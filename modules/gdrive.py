#!/usr/bin/env python3
# -*- compile-command: "cd ..; ./kumodd.py -c config/test.yml -s gdrive -d pdf"; -*-

# windows last mod time is sometimes not preserved.

# For native Google Apps files, kumodd should use the previously saved remote
# file metadata to detect whether the file has changed, using for instance, the
# revision ID.

# Kumodd does not batch requests to the Google Drive API. GD Batch limit is 1000.

from absl import app, flags
from apiclient import errors
from collections import Iterable, OrderedDict
from datetime import datetime
from dateutil import parser
from dumper import dump
from googleapiclient.discovery import build
from hashlib import md5
from jsonpath_ng import jsonpath, parse
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
import csv
import difflib
import httplib2
import io
import json
import logging
import os
import platform
import re
import socket
import socks
import sys
import time
import yaml

if platform.system() == 'Windows':
    from win32 import win32file
    import win32con
    import pywintypes

def name_list_to_format_string( names ):
    """generate a format string for a given list of metadata names"""
    fields = []
    for i, name in enumerate(names):
        if name in ['path']:
            fields.append(f'{{{i}:70.70}}')
        elif name in ['filename', 'id', 'title', 'fullpath']:
            fields.append(f'{{{i}:60.60}}')
        # elif name in ['accTimeMatch']:
        #     fields.append(f'{{{i}:24.24}}')
        elif 'match' in name.lower():
            fields.append(f'{{{i}:9.9}}')
        elif 'md5' in name.lower():
            fields.append(f'{{{i}:32.32}}')
        elif 'Date' in name or name in ['time']:
            fields.append(f'{{{i}:24.24}}')
        elif name in ['fileSize']:
            fields.append(f'{{{i}:9.9}}')
        elif name in ['category', 'shared', 'status']:
            fields.append(f'{{{i}:6.6}}')
        elif name in ['version']:
            fields.append(f'{{{i}:4.4}}')
        else:
            fields.append(f'{{{i}:20.20}}')
    # dump( list( zip( names, fields )))
    return ' '.join( fields )

items_listed = 0
items_downloaded = 0
items_updated = 0
FLAGS = flags.FLAGS
flags.DEFINE_boolean('browser', True, 'open a web browser to authorize access to the google drive account' )
flags.DEFINE_string('config', 'config/config.yml', 'config file', short_name='c')
flags.DEFINE_boolean('revisions', True, 'Download every revision of each file.')
flags.DEFINE_boolean('pdf', True, 'Convert all native Google Apps files to PDF.')
flags.DEFINE_string('gdrive_auth', None, 'Google Drive account authorization file.  Configured in config/config.yml if not specified on command line.')

gdrive_version = "1.0"

def dirname(s):
    index = s.rfind('/')
    if index > 0:
        return s[0:s.rfind('/')]
    return None

def basename(s):
    return s[1 + s.rfind('/'):]

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_google_doc(drive_file):
    return True if re.match( '^application/vnd\.google-apps\..+', drive_file['mimeType'] ) else False

# Convert Y-m-d H:M:S.SSSZ to seconds since the epoch, as a float, with milli-secondsh resolution.
# return zero if attr is missing.
def sec_since_epoch( time_str ):
    return parser.parse( time_str ).timestamp() if time_str else 0.
# return ISO format date string from float seconds since epoch
def epoch_to_iso( sec ):
    return  datetime.utcfromtimestamp(sec).isoformat() + 'Z'

def file_type_from_mime(mimetype):
    file_type = 'other'
    
    if 'application/msword' in mimetype or 'application/vnd.openxmlformats-officedocument.wordprocessingml' in mimetype or 'application/vnd.ms-word' in mimetype or 'application/vnd.google-apps.document' in mimetype:
        file_type = 'doc'
    if 'application/vnd.ms-excel' in mimetype or 'application/vnd.openxmlformats-officedocument.spreadsheetml' in mimetype or 'application/vnd.google-apps.spreadsheet' in mimetype:
        file_type = 'xls'
    if 'application/vnd.ms-powerpoint' in mimetype or 'application/vnd.openxmlformats-officedocument.presentationml' in mimetype or 'application/vnd.google-apps.presentation' in mimetype:
        file_type = 'ppt'
    if 'text/' in mimetype:
        file_type = 'text'
    if 'pdf' in mimetype:
        file_type = 'pdf'
    if 'image/' in mimetype or 'photo' in mimetype or 'drawing' in mimetype:
        file_type = 'image'
    if 'audio/' in mimetype:
        file_type = 'audio'
    if 'video/' in mimetype:
        file_type = 'video'
        
    return file_type
#----------------------------------------------------------------
# The following is intended to create YAML output consistent with 'yq', so
# that external tools can be used to validate metadata.

# As a side effect, the YAML is alos easier to read and diff.

def remove_keys_that_contain( list_of_substrings, dict_in ):
    dict_copy = dict(dict_in)
    for substring in list_of_substrings:
        for key in dict_in:
            if substring in key:
                dict_copy.pop(key, None)
    return dict_copy

def decode_docs(jq_output, json_decoder):
    while jq_output:
        doc, pos = json_decoder.raw_decode(jq_output)
        jq_output = jq_output[pos + 1:]
        yield doc
class OrderedDumper(yaml.SafeDumper):
    pass
def represent_dict_order(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())
OrderedDumper.add_representer(OrderedDict, represent_dict_order)
json_decoder = json.JSONDecoder(object_pairs_hook=OrderedDict)                                    

def dump_yaml( obj, stream ):
    yaml.dump( obj, stream=stream, Dumper=OrderedDumper, width=None, allow_unicode=True, default_flow_style=False)

def yaml_string( obj ):
    stringio = io.StringIO()
    dump_yaml( obj, stringio )
    s = stringio.getvalue()
    stringio.close()
    return s

def redacted_yaml( dict_in ):
    return yaml_string(remove_keys_that_contain(['Link', 'Match', 'status', 'Url', 'yaml'], dict_in))

# get the MD5 digest of the yaml of the metadata dict, excluding the *yaml*, *Url*, and *status* keys
def MD5_of_yaml_of(dict_in):
    return md5(redacted_yaml( dict_in ).encode('utf8')).hexdigest()
#----------------------------------------------------------------
def supplement_drive_file_metadata(service, drive_file, path):
    drive_file['path'] = path

    name = drive_file.get('originalFilename') or drive_file['title'].replace( '/', '_' )
    if drive_file['mimeType'].startswith('application/vnd.google'):
        download_url, extension = get_url_and_ext(drive_file, drive_file)
        if not drive_file.get('fileExtension') and extension:
            drive_file['fileExtension'] = extension
        if not drive_file.get('originalFilename'):
            drive_file['originalFilename'] = name
    else:
        if '.' in name:
            if not drive_file.get('fileExtension'):
                drive_file['extension'] = name[name.rfind('.') + 1:]
            if not drive_file.get('originalFilename'):
                drive_file['originalFilename'] = name
        else:
            if not drive_file.get('fileExtension'):
                drive_file['extension'] = ''
            if not drive_file.get('originalFilename'):
                drive_file['originalFilename'] = name

    drive_file['fullpath'] = drive_file['path'] + '/' + file_name(drive_file)

    revision_list = retrieve_revisions(service, drive_file['id'])
    drive_file['revisions'] = revision_list
    
    drive_file['category'] = file_type_from_mime(drive_file['mimeType'])

    drive_file['label_key'] = ''.join(sorted([(k[0] if v else ' ') for k, v in drive_file['labels'].items()])).upper()

class FileAttr(object):
    def __init__( self, drive_file ):
        self.local_file = local_data_dir( drive_file ) + '/' + file_name(drive_file)
        self.metadata_file = local_metadata_dir( drive_file ) + '/' + file_name(drive_file) + '.yml'
        self.yamlMetadataMD5 = None
        self.update_remote( drive_file )
        self.update_local( drive_file )

    def update_remote( self, drive_file ):
        self.remote_mod_time =	sec_since_epoch( drive_file.get( 'modifiedByMeDate' ))
        self.remote_acc_time =	sec_since_epoch( drive_file.get( 'lastViewedByMeDate' ))

    def update_local( self, drive_file ):
        self.exists = os.path.exists( self.local_file )
        if self.exists:
            self.local_mod_time = os.path.getmtime( self.local_file )
            self.local_acc_time = os.path.getatime( self.local_file )
            self.localSize	= os.path.getsize(self.local_file)
            self.md5Local	= md5(open(self.local_file,'rb').read()).hexdigest()
        else:
            self.yamlMetadataMD5 = None
            self.local_mod_time	= None
            self.local_acc_time	= None
            self.localSize	= None
            self.md5Local	= None
        self.valid = self.local_file_is_valid( drive_file )


    def update_local_metadata_MD5( self ):
        self.metadata_file_exists = os.path.exists( self.metadata_file )
        if self.metadata_file_exists:
            self.yamlMetadataMD5 = MD5_of_yaml_of(yaml.safe_load(open(self.metadata_file,'rb').read()))
        else:
            self.yamlMetadataMD5 = None

    def local_file_is_valid( self, drive_file):
        if not self.exists:
            self.valid =  False
        elif drive_file.get('md5Checksum') != self.md5Local:
            self.valid =  False
        elif self.remote_mod_time != self.local_mod_time:
            self.valid =  False
        elif abs( self.remote_acc_time - self.local_acc_time ) > .001:
            self.valid =  False
        elif int(drive_file.get('fileSize')) != self.localSize:
            self.valid =  False
        else:
            self.valid =  True
        return self.valid

    def compare_metadata_MD5( self, drive_file):
        update_remote_metadata_MD5( drive_file )
        if self.metadata_file_exists:
            if self.yamlMetadataMD5 and self.yamlMetadataMD5 == drive_file.get('yamlMetadataMD5'):
                drive_file['yamlMD5Match'] = 'match'
            else:
                drive_file['yamlMD5Match'] = 'MISMATCH'

    def compare_metadata( self, drive_file ):
        if self.exists:
            if self.remote_mod_time == self.local_mod_time:
                drive_file['modTimeMatch'] = 'match'
            else:
                drive_file['modTimeMatch'] = str(abs(datetime.fromtimestamp(self.local_mod_time) - datetime.fromtimestamp(self.remote_mod_time))).replace(" days, ", " ").replace(" day, ", " ")
    
            if abs( self.remote_acc_time - self.local_acc_time ) < .001:
                drive_file['accTimeMatch'] = 'match'
            else:
                drive_file['accTimeMatch'] = str(abs(datetime.fromtimestamp(self.local_acc_time) - datetime.fromtimestamp(self.remote_acc_time))).replace(" days, ", " ").replace(" day, ", " ")
    
            if drive_file.get('md5Checksum'):
                if drive_file.get('md5Checksum') == self.md5Local:
                    drive_file['md5Match'] = 'match'
                else:
                    drive_file['md5Match'] = 'MISMATCH'
            else:
                drive_file['md5Match'] = 'n/a'            
    
            if drive_file.get('fileSize'):
                drive_file_size = int(drive_file.get('fileSize'))
                if self.localSize == drive_file_size:
                    drive_file['sizeMatch'] = 'match'
                else:
                    drive_file['sizeMatch'] = f"{100.*float(self.localSize)/drive_file_size:f}"
            else:
                drive_file['sizeMatch'] = 'n/a'
    
            if self.valid:
                drive_file['status'] = 'valid'
            else:
                drive_file['status'] = 'INVALID'
        else:
            drive_file['status'] = 'missing'

def update_remote_metadata_MD5(drive_file):
    drive_file['yamlMetadataMD5'] = MD5_of_yaml_of(drive_file)


# return a list of values
# object_path_list is a list of strings, [ 'foo.bar' ] 
def get_dict_values( obj, object_path_list ):
    result = []
    for name in object_path_list:
        if '.' in name :
            elem = parse(name).find( obj )[0].value
        else:
            elem = obj.get(name)
        if elem is None:
            elem = ''
        result.append( elem )
    return result

def print_file_metadata(service, drive_file, path, writer, metadata_names, output_format=None):
    global items_listed
    supplement_drive_file_metadata(service, drive_file, path)
    file_attr = FileAttr( drive_file )
    file_attr.compare_metadata( drive_file )
    file_attr.update_local_metadata_MD5()
    file_attr.compare_metadata_MD5(drive_file)

    data = get_dict_values( drive_file, metadata_names )
    if writer:
        writer.writerow( data )
    items_listed += 1
    if output_format:
        print( output_format.format( *[str(i) for i in data] ))

    if ( drive_file.get('yamlMD5Match') == 'MISMATCH' and
        file_attr.metadata_file_exists ):
        print(22*'_', file_attr.metadata_file)
        diff = difflib.ndiff(
            redacted_yaml(drive_file).splitlines(keepends=True),
            redacted_yaml(yaml.safe_load(open(file_attr.metadata_file,'rb').read())).splitlines(keepends=True))
        print( ''.join( list( diff )), end="")
        print(79*'_')
    
def download_file_and_metadata(service, drive_file, path, writer, metadata_names, output_format=None):
    global items_updated
    supplement_drive_file_metadata(service, drive_file, path)
    file_attr = FileAttr( drive_file )

    # dump( file_attr )
    if not file_attr.valid:
        if download_file( service, drive_file ):
            items_updated += 1
            file_attr.update_local( drive_file )
            file_attr.compare_metadata( drive_file )
            save_metadata(drive_file)
            file_attr.update_local_metadata_MD5()
            file_attr.compare_metadata_MD5( drive_file )
        else:
            logging.critical( f"failed to download: {local_data_dir( drive_file ) + '/' + file_name(drive_file)}: {e}")
    file_attr.compare_metadata( drive_file )
    file_attr.update_local_metadata_MD5()
    file_attr.compare_metadata_MD5( drive_file )

    data = get_dict_values( drive_file, metadata_names )

    if writer:
        writer.writerow( data )
    if output_format:
        print( output_format.format( *[str(i) for i in data] ))
    if drive_file.get('yamlMD5Match') == 'MISMATCH':
        print(44*'_', drive_file['title'])
        diff = difflib.ndiff(
            redacted_yaml(drive_file).splitlines(keepends=True),
            redacted_yaml(yaml.safe_load(open(file_attr.metadata_file,'rb').read())).splitlines(keepends=True))
        print( ''.join( list( diff )), end="")
        print(79*'_')

def save_metadata(drive_file):
    metadata_path = local_metadata_dir( drive_file ) + '/' + file_name(drive_file) + '.yml'
    ensure_dir(dirname(metadata_path))
    yaml.dump(drive_file, open(metadata_path, 'w+'), Dumper=yaml.Dumper)

def get_user_info(service):
    """Print information about the user along with the Drive API settings.

  Args:
    service: Drive API service instance.
  """
    try:
        about = service.about().get().execute()
        return about
    except errors.HttpError as error:
        print( f'Request for google about() failed: {e}' )
        return None
        
def reset_file(filename):
    open(filename, "w").close()

def is_file(item):
    return item['mimeType'] != 'application/vnd.google-apps.folder'
    
def is_folder(item):
    return item['mimeType'] == 'application/vnd.google-apps.folder'
        

def walk_folder_metadata( service, http, folder, writer=None, metadata_names=None, output_format=None, base_path='.', depth=0 ):
    param = {'q': f"'{folder['id']}' in parents" }   # first page

    while True: # repeat for each page
        try:
            file_list = service.files().list(**param).execute()
        except Exception as e:
            print( f'cautght: {e}' )
            logging.critical( f"Couldn't get contents of folder {file_list['title']}", exc_info=True)

        
        folder_items = file_list['items']
        path = base_path + '/' + folder['title'].replace( '/', '_' )
    
        if FLAGS.list:
            for item in filter(is_file, folder_items):
                if (
                    ( FLAGS.list == 'all' )
                    or
                    (   ( FLAGS.list in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other']
                         and FLAGS.list == file_type_from_mime(item['mimeType']) ))
                    or 
                    (  ( FLAGS.list == 'office'
                        and file_type_from_mime(item['mimeType']) in ['doc', 'xls', 'ppt']))
                        ):
                    print_file_metadata(service, item, path, writer, metadata_names, output_format)

        if FLAGS.download:    
            ensure_dir(FLAGS.destination + '/' + username + '/' + path)
            for item in filter(is_file, folder_items):
                if (
                    ( FLAGS.download == 'all' )
                    or 
                    ( ( FLAGS.download in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other'] )
                     and FLAGS.download == file_type_from_mime(item['mimeType']) )
                    or
                    ( FLAGS.download == 'office'
                     and file_type_from_mime(item['mimeType']) in ['doc', 'xls', 'ppt'])
                     ):
                    download_file_and_metadata(service, item, path, writer, metadata_names, output_format)

        for item in filter(is_folder, folder_items):
            walk_folder_metadata( service, http, item, writer, metadata_names, output_format, path, depth+1 )
            
        if file_list.get('nextPageToken'):
            param['pageToken'] = file_list.get('nextPageToken')
        else:
            break


def download_listed_files(service, http, config, metadata_names=None, output_format=None):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    local_base_path = FLAGS.destination + '/' + username
    with open(FLAGS.usecsv[0], 'rt') as csv_handle:
        reader = csv.reader(csv_handle)
        header = next(reader, None)
        index_of_path = header.index( config.get('csv_title',{}).get('path'))
        index_of_id = header.index( config.get('csv_title',{}).get('id'))
        for row in reader:
            path = dirname(row[index_of_path])
            try:
                drive_file = service.files().get(fileId=row[index_of_id]).execute()
            except Exception as e:
                print( f'cautght: {e}' )
                logging.critical( f"Request Failed for: {row}", exc_info=True)
            download_file_and_metadata(service, drive_file, path, None, metadata_names, output_format)

def download_revision(service, drive_file, revision):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    file_id = drive_file['id']
    
    try:
        revision = service.revisions().get(fileId=file_id, revisionId=revision['id']).execute()
    except Exception as e:
        print( f'cautght: {e}' )
        logging.critical( f"Request Failed for: {revision}", exc_info=True)
    download_url, extension = get_url_and_ext(drive_file, revision)
    file_location = local_data_dir( drive_file ) + '/' + file_name(drive_file, revision)

    if download_url:
        try:
            resp, content = service._http.request(download_url)
        except Exception as e:
            print( f'cautght: {e}' )
            logging.critical( f"Request Failed for: {download_url}", exc_info=True)
        if resp.status == 200:
            try:
                with open( file_location, 'wb+' ) as handle:
                    handle.write( content )
            except Exception as e:
                print( f'cautght: {e}' )
                logging.critical( f"{file_location} Could not open file %s for writing. Please check permissions.", exc_info=True)
                return False
            return True
        else:
            logging.critical( resp )
            return False
    else:
        return False
    
def retrieve_revisions(service, file_id):
    """Retrieve a list of revisions.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to retrieve revisions for.
    Returns:
    List of revisions.
    """
    try:
        revisions = service.revisions().list(fileId=file_id).execute()
    except Exception as e:
        print( f'cautght: {e}' )
        logging.critical( f"Request Failed for: {file_id}", exc_info=True)
    if len(revisions.get('items', [])) > 1:
        return revisions.get('items', [])
    return None    


def get_url_and_ext(drive_file, revision):
    if is_google_doc(drive_file):
        if FLAGS.pdf:
            download_url = revision['exportLinks']['application/pdf']
            extension = 'pdf'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.document':
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.text']
            extension = 'odt'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.presentation':
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.presentation']
            extension = 'odp'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            # was: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.spreadsheet']
            extension = 'ods'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.drawing':
            # was: image/jpeg
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.graphics']
            extension = 'odg'
        else:
            download_url = revision['exportLinks']['application/pdf']
            extension = '.pdf'
    else:
        download_url = revision['downloadUrl']
        extension = ''
    return [download_url, extension]

def local_data_dir( drive_file ):
    return '/'.join([ FLAGS.destination, username, drive_file['path'] ])

def file_name( drive_file, revision=None ):
    name = drive_file['originalFilename']
    if drive_file.get('fileExtension'):
        name = name[0:name.rfind('.' + drive_file['fileExtension'])]
    if int(drive_file.get('version', 1)) > 1:
        name += f"({drive_file['version']})"
    if revision:
        name += f"_({revision['id']:0>4}_{revision['modifiedDate']})"
    if drive_file.get('fileExtension'):
        name += '.' + drive_file['fileExtension']
    return name

def local_metadata_dir( drive_file ):
    return '/'.join([ FLAGS.metadata_destination, username, drive_file['path'] ])


def download_file( service, drive_file ):
    """Download a file's content.

    Args:
      service: Drive API service instance.
      drive_file: Drive File instance.
    
    Returns:
      True if successful, else False.
    """
    
    download_url, extension = get_url_and_ext(drive_file, drive_file)
    file_path = local_data_dir( drive_file ) + '/' + file_name(drive_file)

    if not download_url:
        return False
    else:
        if FLAGS.revisions:
            revision_list = drive_file.get('revisions')
            if revision_list:
                for revision in revision_list[1:len(revision_list)]:
                    download_revision(service, drive_file, revision)
        
        while True:
            try:
                resp, content = service._http.request(download_url)
            except Exception as e:
                logging.critical( f"Exception {e} while reading {file_path}. Retrying...", exc_info=True)
                continue
            if resp.status == 200:
                try:
                    with open( file_path, 'wb+' ) as handle:
                        handle.write( content )
                except e:
                    logging.critical( f"Cannot open {file_path} for writing: {e}", exc_info=True)
                    return False

                try:
                    # time stamps set on exported files
                    modify_time = sec_since_epoch( drive_file.get( 'modifiedByMeDate' ))
                    access_time = sec_since_epoch( drive_file.get( 'lastViewedByMeDate' ))
                    create_time = sec_since_epoch( drive_file.get( 'createdDate' ))

                    if platform.system() == 'Windows':
                        # API to set create timestamp is not cross-platform
                        # Setting the modify and access time is unreliable via SetFileTIme, so we only set create.
                        handle = win32file.CreateFile(
                            file_path, win32con.GENERIC_WRITE,
                            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                            None, win32con.OPEN_EXISTING,
                            win32con.FILE_ATTRIBUTE_NORMAL, None)
                        win32file.SetFileTime(handle, pywintypes.Time(create_time), None, None, UTCTimes=True)
                        handle.close()
                    os.utime(file_path, (access_time, modify_time))

                except Exception as e:
                    logging.critical( f"While setting file times, got exception: {e}", exc_info=True)
                finally:
                    handle.close()

                return True
            else:
                logging.critical( resp )
                return False


def main(argv):
    # Let the flags module process the command-line arguments
    try:
        argv = FLAGS(argv)
    except flags.FlagsError as e:
        print( f'{e}\\nUsage: {argv[0]} ARGS\\n{FLAGS}' )
        sys.exit(1)

    if FLAGS.config.find('/'):
        ensure_dir(dirname(FLAGS.config))
    if not os.path.exists(FLAGS.config):
        yaml.dump(yaml.safe_load('''
gdrive:
  csv_prefix: ./filelist-
  gdrive_auth: config/gdrive_config.json
  oauth_id: config/gdrive.dat
  csv_columns: title,category,modTimeMatch,md5Match,revision,ownerNames,fileSize,modifiedByMeDate,createdDate,mimeType,path,id,lastModifyingUserName,md5Checksum,md5Local,modifiedByMeDate,lastViewedByMeDate,shared

csv_title:
  accTimeMatch: Acc Time
  app: Application
  appDataContents: App Data
  capabilities: Capabilities
  category: Category
  copyRequiresWriterPermission: CopyRequiresWriterPermission
  copyable: Copyable
  createdDate: Created (UTC)
  downloadUrl: Download
  editable: Editable
  embedLink: Embed
  etag: Etags
  explicitlyTrashed: Trashed
  exportLinks: Export
  fileExtension: EXT
  fileSize: Size(bytes)
  fullpath: Full Path
  headRevisionId: HeadRevisionId
  iconLink: Icon Link
  id: File Id
  kind: Kind
  labels: Labels
  lastModifyingUserName: Last Mod By
  lastViewedByMeDate: My Last View
  local_path: Local Path
  md5Checksum: MD5
  md5Local: Local MD5
  md5Match: MD5s
  mimeType: MIME Type
  modTimeMatch: Mod Time
  modifiedByMeDate: My Last Mod (UTC)
  modifiedDate: Last Modified (UTC)
  originalFilename: Original File Name
  ownerNames: Owner
  owners: Owners
  parents: Parents
  path: Path
  quotaBytesUsed: Quota Used
  revision: Revisions
  selfLink: Self Link
  shared: Shared
  sizeMatch: Size
  spaces: Spaces
  status: Status
  thumbnailLink: Thumbnail
  time: Time (UTC)
  title: Name
  user: User
  userPermission: User Permission
  version: Version
  webContentLink: Web Link
  writersCanShare: CanShare
'''),
                  io.open(FLAGS.config, 'w', encoding='utf8'), Dumper=yaml.Dumper,
                  default_flow_style=False, allow_unicode=True)

    config = yaml.safe_load(open(FLAGS.config, 'r'))

    # Set the logging according to the command-line flag
    logging.basicConfig(level=FLAGS.log, format='%(asctime)s %(levelname)s %(message)s', datefmt='%y-%b-%d %H:%M:%S')
    if config.get('log_to_stdout'):
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(FLAGS.log)
        handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        logging.getLogger().addHandler(handler)
        httplib2.debuglevel = -1
    logging.getLogger().setLevel(FLAGS.log)

    api_credentials_file = FLAGS.gdrive_auth or config.get('gdrive',{}).get('gdrive_auth')
    metadata_names = (config.get('gdrive',{}).get('csv_columns')).split(',')

    # Set up a Flow object that opens a web browser or prints a URL for
    # approval of access to the given google drive account.
    FLOW = flow_from_clientsecrets(api_credentials_file,
                                   scope= 'https://www.googleapis.com/auth/drive',
                                   message= f"""
ERROR: missing OAuth 2.0 credentials.

To use kumodd, you must download a Google a API credentials file and store it as:

{os.path.join(os.path.dirname(__file__), api_credentials_file)}

To obtain a credentials file, refer to the kumodd README, and visit the Google APIs Console at:
https://code.google.com/apis/console

""")
    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.

    if isinstance(config.get('proxy'),dict):
        proxy = config.get('proxy')
        try:
            proxy_uri = 'http://' + proxy.get('host')
            if 'port' in proxy:
                proxy_uri += ':' + proxy.get('port')
            resp, content = http.request(proxy_uri, "GET")
        except Exception as e:
            print(f"\nCannot connect to proxy at: {proxy_uri}.  Please check your network.\n\n")
            return
        http = httplib2.Http(
            disable_ssl_certificate_validation=True,
            proxy_info = httplib2.ProxyInfo(
                httplib2.socks.PROXY_TYPE_HTTP,
                proxy_host = proxy.get('host'),
                proxy_port = int(proxy.get('port')) if proxy.get('port') else None,
                proxy_user = proxy.get('user'),
                proxy_pass = proxy.get('pass') ))
    else:
        http = httplib2.Http()

    try:
        resp, content = http.request("http://google.com", "GET")
    except Exception as e:
        print(f"""\nCannot connect to google.com.  Please check your network.

Error: {e}\n""" )
        return

    # If the Google Drive credentials don't exist or are invalid run the client
    # flow, and store the credentials.
    oauth_id = config.get('gdrive',{}).get('oauth_id')
    try:
        storage = Storage(oauth_id)
        credentials = storage.get()
    except:
        open(oauth_id, "a+").close()     # ensure oauth_id exists
        storage = Storage(oauth_id)
        credentials = None

    if credentials is None or credentials.invalid:
        oflags = argparser.parse_args([])
        oflags.noauth_local_webserver = not FLAGS.browser
        credentials = run_flow(FLOW, storage, oflags, http)
    http = credentials.authorize(http)

    service = build("drive", "v2", http=http)
    user_info = get_user_info(service)
    
    global username
    
    if user_info != None:
        username = user_info['user']['emailAddress']
    else:
        username = '???'
    ensure_dir(FLAGS.destination + '/' + username)
    output_format = name_list_to_format_string( metadata_names )

    try:
        start_time = datetime.now()
        if FLAGS.list:
            print( output_format.format( *[ config.get('csv_title',{}).get(name) or name for name in metadata_names ]))
            csv_prefix = config.get('gdrive',{}).get('csv_prefix')
            if csv_prefix.find('/'):
                ensure_dir(dirname(csv_prefix))
            with open(config.get('gdrive',{}).get('csv_prefix') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ config.get('csv_title').get(name) for name in metadata_names ] )
                try:
                    start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
                except Exception as e:
                    print( f"Request Failed for: {FLAGS.drive_id}")
                    logging.critical( f"Request Failed for: {FLAGS.drive_id}", exc_info=True)
                walk_folder_metadata( service, http, start_folder, writer, metadata_names, output_format)
            print(f'\n{items_downloaded} files downloaded and {items_updated} updated from {username}')

        elif FLAGS.download:
            print('download files')
            print( output_format.format( *[ config.get('csv_title').get(name) or name for name in metadata_names ]))
            try:
                start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            except Exception as e:
                print( f"Request Failed for: {FLAGS.drive_id}")
                logging.critical( f"Request Failed for: {FLAGS.drive_id}", exc_info=True)
            with open(config.get('gdrive',{}).get('csv_prefix') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ config.get('csv_title').get(name) for name in metadata_names ] )
                walk_folder_metadata( service, http, start_folder, writer, metadata_names, output_format)
            print(f'\n{items_downloaded} files downloaded and {items_updated} updated from {username}')

        elif FLAGS.usecsv:
            print('download listed files')
            header = output_format.format( *[ config.get('csv_title').get(name) for name in metadata_names ])
            print( header )
            download_listed_files(service, http, config, metadata_names, output_format)
            print('\n' + str(items_downloaded) + ' files downloaded and ' + str(items_updated) + ' updated from ' + username + ' drive')

        end_time = datetime.now()
        print(f'Duration: {end_time - start_time}')
    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run the application to re-authorize")

if __name__ == '__main__':
    app.run(main)
