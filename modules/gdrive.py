# -*- compile-command: "cd .. ;./kumodd.py -c config/test.yml -d doc|cut -c 1-110"; -*-
__author__ = 'andrsebr@gmail.com (Andres Barreto), rich.murphey@gmail.com'

# Todo

# use the latest last access time.

# windows last mod time is sometimes not preserved.

# For native Google Apps files, kumodd should use the previously saved remote file
# metadata to detect whether the file has changed, using for instance, the revision
# number.

# Kumodd does not batch requests to the Google Drive API. Batch limit is 1000.

from absl import app, flags
from apiclient import errors
from collections import Iterable
from datetime import datetime
from googleapiclient.discovery import build
from hashlib import md5
from jsonpath_ng import jsonpath, parse
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
from pprint import pprint
import csv
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
        if 'path' in name:
            fields.append(f'{{{i}:70.70}}')
        elif name in ['id', 'title']:
            fields.append(f'{{{i}:44.44}}')
        elif name in ['md5Checksum', 'md5Local']:
            fields.append(f'{{{i}:32.32}}')
        elif 'Date' in name or name in ['time']:
            fields.append(f'{{{i}:24.24}}')
        elif name in ['md5Match', 'modTimeMatch', 'sizeMatch']:
            fields.append(f'{{{i}:9.9}}')
        elif name in ['category', 'revision', 'shared', 'fileSize', 'status', 'version']:
            fields.append(f'{{{i}:6.6}}')
        else:
            fields.append(f'{{{i}:20.20}}')
    return ' '.join( fields )

items_listed = 0
items_downloaded = 0
items_updated = 0
FLAGS = flags.FLAGS
flags.DEFINE_boolean('browser', True, 'open a web browser to authorize access to the google drive account' )
flags.DEFINE_string('config', 'config/config.yml', 'config file', short_name='c')
flags.DEFINE_boolean('revisions', True, 'Download every revision of each file.')
flags.DEFINE_boolean('pdf', False, 'Convert all native Google Apps files to PDF.')
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

def local_file_is_valid(drive_file):
    if os.path.exists( drive_file['local_path'] + drive_file['extension'] ):
        # Drive API provides time to milliseconds. 2019-06-24T05:41:17.095Z
        remote_mod_time = time.mktime( time.strptime( drive_file['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ' ) )
        # float seconds since the epoch. Actualresolution depends on the file-system.
        local_mod_time = os.path.getmtime( drive_file['local_path'] + drive_file['extension'] )
        tdiff = abs(float(remote_mod_time) - float(local_mod_time))
        if tdiff < 1.0:
            return False

        if drive_file.get('md5Checksum'):
            local_md5 = md5(open(drive_file['local_path'] + drive_file['extension'],'rb').read()).hexdigest()
            if drive_file.get('md5Checksum') == local_md5:
                return False
    return True

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

def supplement_drive_file_metadata(service, drive_file, path):
    # Note: thumbnailLink change each time the metadata is retrieved, which
    # means a file's metadata changes without any changes to the file. Because
    # this interferes with verifying the rest of the metadata, we remove it
    # from the metadata that is preserved locally.
    drive_file.pop('thumbnailLink', None)

    remote_path = path + '/' + drive_file['title'].replace( '/', '_' )
    drive_file['path'] = remote_path

    download_url, extension = get_url_and_ext(drive_file, drive_file)
    drive_file['extension'] = extension

    local_path = FLAGS.destination + '/' + username + '/' + remote_path
    drive_file['local_path'] = local_path

    revision_list = retrieve_revisions(service, drive_file['id'])
    drive_file['revisions'] = revision_list

    revision = str(len(revision_list)) if revision_list else '1'
    drive_file['revision'] = revision
    
    drive_file['category'] = file_type_from_mime(drive_file['mimeType'])

    drive_file['label_key'] = ''.join(sorted([(k[0] if v else ' ') for k, v in drive_file['labels'].items()])).upper()

    if os.path.exists( drive_file['local_path'] + drive_file['extension'] ):
        # Drive API provides time to milliseconds. 2019-06-24T05:41:17.095Z
        remote_mod_time = time.mktime( time.strptime( drive_file['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ' ) )
        # float seconds since the epoch. Actualresolution depends on the file-system.
        local_mod_time = os.path.getmtime( drive_file['local_path'] + drive_file['extension'] )
        tdiff = abs(float(remote_mod_time) - float(local_mod_time))
        if tdiff < 1.0:   # timestamps match within one second
            drive_file['modTimeMatch'] = 'match'
        else:
            drive_file['modTimeMatch'] = str(abs(datetime.fromtimestamp(local_mod_time) - datetime.fromtimestamp(remote_mod_time))).replace(" days, ", " ").replace(" day, ", " ")

        drive_file['md5Local'] = md5(open(drive_file['local_path'] + drive_file['extension'],'rb').read()).hexdigest()
        if drive_file.get('md5Checksum'):
            if drive_file.get('md5Checksum') == drive_file['md5Local']:
                drive_file['md5Match'] = 'match'
            else:
                drive_file['md5Match'] = 'MISMATCH'
        else:
            drive_file['md5Match'] = 'n/a'            

        if drive_file.get('fileSize'):
            drive_file['localSize'] = str(os.path.getsize(drive_file['local_path'] + drive_file['extension']))
            if drive_file['localSize'] == drive_file.get('fileSize'):
                drive_file['sizeMatch'] = 'match'
            else:
                drive_file['sizeMatch'] = f"{100.*float(drive_file['localSize'])/float(drive_file.get('fileSize')):f}"
                # 'MISMATCH'
        else:
            drive_file['sizeMatch'] = 'n/a'

        if (( not drive_file.get('fileSize') or (drive_file['sizeMatch'] == 'match'))
            and
            ( not drive_file.get('md5Checksum') or (drive_file['md5Match'] == 'match'))
            and
            ( drive_file['modTimeMatch'] == 'match' )):
            drive_file['status'] = 'valid'
        else:
            drive_file['status'] = 'INVALID'
    else:
        drive_file['status'] = 'missing'


def list_from_metadata_names( obj, metadata_names ):
    result = []
    for name in metadata_names:
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
    data = list_from_metadata_names( drive_file, metadata_names )
    if writer:
        writer.writerow( data )
    items_listed += 1
    if output_format:
        print( output_format.format( *[str(i) for i in data] ))
    
def download_file_and_metadata(service, drive_file, path, writer, metadata_names, output_format=None):
    global items_updated
    supplement_drive_file_metadata(service, drive_file, path)

    if ((drive_file.get('md5Checksum') and (drive_file.get('md5Match') != 'match')) or
        (drive_file.get('modTimeMatch') != 'match')):
        if download_file( service, drive_file ):
            drive_file['status'] = 'update'
            items_updated += 1
            save_metadata(drive_file)
        else:
            drive_file['status'] = 'error'
            logging.critical( f"downloading: {drive_file['local_path'] + drive_file['extension']}" )
    else:
        drive_file['status'] = 'verify'
    data = list_from_metadata_names( drive_file, metadata_names )
    if writer:
        writer.writerow( data )
    if output_format:
        print( output_format.format( *[str(i) for i in data] ))


def save_metadata(drive_file):
    metadata_path = FLAGS.metadata_destination + '/' + username + '/' +  drive_file['path'] + '.yml'
    ensure_dir(dirname(metadata_path))
    with open(metadata_path, 'w+') as handle:
        yaml.dump(drive_file, handle, Dumper=yaml.Dumper)

def get_user_info(service):
    """Print information about the user along with the Drive API settings.

  Args:
    service: Drive API service instance.
  """
    try:
        about = service.about().get().execute()
        return about
    except errors.HttpError as error:
        print( 'An error occurred: %s' % error )
        return None
        
def reset_file(filename):
    open(filename, "w").close()

def is_file(item):
    return item['mimeType'] != 'application/vnd.google-apps.folder'
    
def is_folder(item):
    return item['mimeType'] == 'application/vnd.google-apps.folder'
        

def walk_folder_metadata( service, http, folder, writer=None, metadata_names=None, output_format=None, base_path='.', depth=0 ):
    param = {'q': f"'{folder['id']}' in parents" }

    while True:
        try:
            # exceptions are defined in
            # https://github.com/googleapis/google-api-python-client/blob/master/googleapiclient/errors.py
            file_list = service.files().list(**param).execute()
        except (urllib.errors.HTTPError, http.client.IncompleteRead):
            continue
        except Exception as e:
            print( f'cautght: {e}' )
            logging.critical( f"Couldn't get contents of folder {file_list['title']}", exc_info=True)
        folder_items = file_list['items']
        path = base_path + '/' + folder['title'].replace( '/', '_' )
    
        if FLAGS.list_items:
            for item in filter(is_file, folder_items):
                if (
                    ( FLAGS.list_items == 'all' )
                    or
                    (   ( FLAGS.list_items in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other']
                         and FLAGS.list_items == file_type_from_mime(item['mimeType']) ))
                    or 
                    (  ( FLAGS.list_items == 'office'
                        and file_type_from_mime(item['mimeType']) in ['doc', 'xls', 'ppt']))
                        ):
                    print_file_metadata(service, item, path, writer, metadata_names, output_format)

        if FLAGS.get_items:    
            ensure_dir(FLAGS.destination + '/' + username + '/' + path)
            for item in filter(is_file, folder_items):
                if (
                    ( FLAGS.get_items == 'all' )
                    or 
                    ( ( FLAGS.get_items in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other'] )
                     and FLAGS.get_items == file_type_from_mime(item['mimeType']) )
                    or
                    ( FLAGS.get_items == 'office'
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
            while True:
                try:
                    drive_file = service.files().get(fileId=row[index_of_id]).execute()
                except (urllib.errors.HTTPError, http.client.IncompleteRead):
                    continue
                break
            download_file_and_metadata(service, drive_file, path, None, metadata_names, output_format)

def download_revision(service, drive_file, revision_id):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    file_id = drive_file['id']
    
    while True:
        try:
            revision = service.revisions().get(fileId=file_id, revisionId=revision_id).execute()
        except (urllib.errors.HTTPError, http.client.IncompleteRead):
            continue
        break

    download_url, extension = get_url_and_ext(drive_file, revision)
    file_location = drive_file['local_path'] + f"_({revision_id:0>4}_{revision['modifiedDate']}){drive_file['extension']}"

    if download_url:
        while True:
            try:
                resp, content = service._http.request(download_url)
            except (urllib.errors.HTTPError, httplib2.IncompleteRead):
                continue
            break

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
    while True:
        try:
            revisions = service.revisions().list(fileId=file_id).execute()
        except (urllib.errors.HTTPError, httplib2.IncompleteRead):
            continue
        break
    if len(revisions.get('items', [])) > 1:
        return revisions.get('items', [])
    return None    


def get_url_and_ext(drive_file, revision):
    if is_google_doc(drive_file):
        if FLAGS.pdf:
            download_url = revision['exportLinks']['application/pdf']
            extension = '.pdf'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.document':
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.text']
            extension = '.odt'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.presentation':
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.presentation']
            extension = '.odp'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            # was: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.spreadsheet']
            extension = '.ods'
        elif drive_file['mimeType'] == 'application/vnd.google-apps.drawing':
            # was: image/jpeg
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.graphics']
            extension = '.odg'
        else:
            download_url = revision['exportLinks']['application/pdf']
            extension = '.pdf'
    else:
        download_url = revision['downloadUrl']
        extension = ''
    return [download_url, extension]

def download_file( service, drive_file ):
    """Download a file's content.

    Args:
      service: Drive API service instance.
      drive_file: Drive File instance.
    
    Returns:
      True if successful, else False.
    """
    
    download_url, extension = get_url_and_ext(drive_file, drive_file)

    if not download_url:
        return False
    else:
        if FLAGS.revisions:
            revision_list = drive_file.get('revisions')
            if revision_list:
                for revision in revision_list[1:len(revision_list)-1]:
                    download_revision(service, drive_file, revision['id'])
        
        while True:
            try:
                resp, content = service._http.request(download_url)
            except (urllib.errors.HTTPError, httplib2.IncompleteRead) as e:
                logging.critical( f"Exception {e} while reading {drive_file['local_path'] + drive_file['extension']}. Retrying...", exc_info=True)
                continue
            if resp.status == 200:
                try:
                    with open( drive_file['local_path'] + drive_file['extension'], 'wb+' ) as handle:
                        handle.write( content )
                except e:
                    logging.critical( f"Cannot open {drive_file['local_path'] + drive_file['extension']} for writing: {e}", exc_info=True)
                    return False

                def date_or_zero( file, attr ):
                    return time.strptime( file[attr], '%Y-%m-%dT%H:%M:%S.%fZ' ) if file.get(attr) else 0.
                try:
                    # time stamps set on exported files
                    modify_time = time.mktime( date_or_zero( drive_file, 'modifiedDate' ))
                    access_time = time.mktime( date_or_zero( drive_file, 'markedViewedByMeDate' ))
                    create_time = time.mktime( date_or_zero( drive_file, 'createdDate' ))
    
                    if platform.system() == 'Windows':
                        # API to set create timestamp is not cross-platform
                        # Setting the modify and access time is unreliable via SetFileTIme, so we only set create.
                        handle = win32file.CreateFile(
                            drive_file['local_path'] + drive_file['extension'], win32con.GENERIC_WRITE,
                            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
                            None, win32con.OPEN_EXISTING,
                            win32con.FILE_ATTRIBUTE_NORMAL, None)
                        win32file.SetFileTime(handle, pywintypes.Time(create_time), None, None, UTCTimes=True)
                        handle.close()
                    os.utime(drive_file['local_path'] + drive_file['extension'], (access_time, modify_time))

                except Exception as e:
                    logging.critical( f"While setting file times, got exception: {e}", exc_info=True)
                finally:
                    handle.close()

                # recheck MD5, modify time and file size
                supplement_drive_file_metadata(service, drive_file, dirname(drive_file['path']))

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
  csv_columns: title,category,modTimeMatch,md5Match,revision,ownerNames,fileSize,modifiedDate,createdDate,mimeType,path,id,lastModifyingUserName,md5Checksum,md5Local,modifiedByMeDate,lastViewedByMeDate,shared

csv_title:
  app: Application
  category: Category
  createdDate: Created (UTC)
  fileSize: Bytes
  id: File Id
  index: Index
  lastModifyingUserName: Modified by
  lastViewedByMeDate: My Last View
  local_path: Local Path
  md5Checksum: MD5
  md5Local: Local MD5
  md5Match: MD5s
  mimeType: MIME Type
  modTimeMatch: Mod Time
  modifiedByMeDate: My Last Mod
  modifiedDate: Last Modified (UTC)
  ownerNames: Owner
  path: Remote Path
  revision: Revisions
  shared: Shared
  status: Status
  time: Time (UTC)
  title: Name
  user: User
  version: Version
'''),
                  io.open(FLAGS.config, 'w', encoding='utf8'), Dumper=yaml.Dumper,
                  default_flow_style=False, allow_unicode=True)

    config = yaml.safe_load(open(FLAGS.config, 'r'))

    # Set the logging according to the command-line flag
    logging.basicConfig(level=FLAGS.log, format='%(asctime)s %(levelname)s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    if config.get('log_to_stdout'):
        with logging.StreamHandler(sys.stdout) as handler:
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
        if FLAGS.list_items:
            print( output_format.format( *[ config.get('csv_title',{}).get(name) or name for name in metadata_names ]))
            csv_prefix = config.get('gdrive',{}).get('csv_prefix')
            if csv_prefix.find('/'):
                ensure_dir(dirname(csv_prefix))
            with open(config.get('gdrive',{}).get('csv_prefix') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ config.get('csv_title').get(name) for name in metadata_names ] )
                while True:
                    try:
                        start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
                    except (urllib.errors.HTTPError, httplib2.IncompleteRead):
                        continue
                    break
                walk_folder_metadata( service, http, start_folder, writer, metadata_names, output_format)
            print(f'\n{items_downloaded} files downloaded and {items_updated} updated from {username}')

        elif FLAGS.get_items:
            print('download files')
            print( output_format.format( *[ config.get('csv_title').get(name) or name for name in metadata_names ]))
            while True:
                try:
                    start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
                except (urllib.errors.HTTPError, httplib2.IncompleteRead):
                    continue
                break
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
