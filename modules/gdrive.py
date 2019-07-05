# -*- compile-command: "cd .. ;./kumodd.py -c config/test.yml -l doc"; -*-
"""Simple command-line sample for the Google Drive API.

Command-line application that retrieves the list of files in google drive.

Usage:
    $ python drive.py

You can also get help on all the command-line flags the program understands
by running:

    $ python drive.py --help

To get detailed log output run:

    $ python drive.py --log=DEBUG
"""

__author__ = 'andrsebr@gmail.com (Andres Barreto)'

from absl import flags
import httplib2
import socks
import logging
import os
import io
import pprint
import sys
import re
import time
import yaml
import csv
import socket
import platform
from hashlib import md5
from collections import Iterable
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
from oauth2client.tools import run_flow, argparser
from jsonpath_ng import jsonpath, parse
#---
from apiclient import errors
import json
from datetime import datetime

def name_list_to_format_string( names ):
    """generate a format string for a given list of metadata names"""
    fields = []
    for i, name in enumerate(names):
        if 'path' in name:
            fields.append(f'{{{i}:70}}')
        elif name in ['id']:
            fields.append(f'{{{i}:44}}')
        elif name in ['md5', 'title']:
            fields.append(f'{{{i}:32}}')
        elif 'Date' in name or name in ['time']:
            fields.append(f'{{{i}:24}}')
        elif name in ['category', 'revision', 'shared', 'size', 'status', 'version']:
            fields.append(f'{{{i}:6}}')
        else:
            fields.append(f'{{{i}:20}}')
    return ' '.join( fields )

items_listed = 0
items_downloaded = 0
items_updated = 0
FLAGS = flags.FLAGS
flags.DEFINE_boolean('no_browser', False, 'disable launching a web browser to authorize access to a google drive account' )
flags.DEFINE_string('config', 'config/config.yml', 'config file', short_name='c')

gdrive_version = "1.0"

def get_path(mydict, path):
    """ get_path({a: {b; 1, c:2}}, 'a.c' ) -> '2'    """
    elem = mydict
    try:
        for x in path.strip(".").split("."):
            try:
                x = int(x)
                elem = elem[x]
            except ValueError:
                elem = elem.get(x)
    except:
        pass
    return elem


def list_from_metadata_names( obj, metadata_names ):
    result = []
    for name in metadata_names:
        if '.' in name :
            elem = parse(name).find( obj )[0].value
        else:
            elem = obj.get(name)
        result.append( elem )
    return result

# print( str( list_from_metadata_names( {'a': {'b': 1, 'c':2}}, ['a.c', 'a.b'] )))
# sys.exit(1)

def maybe_flatten(maybe_list, separator=' '):
    """return concatenated string from items, possibly nested."""
    if isinstance(maybe_list, Iterable) and not isinstance(maybe_list, (str, bytes)):
        return separator.join([ maybe_flatten(x) for x in maybe_list ])
    else:
        return str(maybe_list)

# The flags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.


def open_logfile():
    if not re.match( '^/', FLAGS.logfile ):
        FLAGS.logfile = FLAGS.destination + '/' + username + '/' + FLAGS.logfile
    global LOG_FILE
    LOG_FILE = open( FLAGS.logfile, 'a' )
    
def log(str):
    LOG_FILE.write( (str + '\n') )

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

import os
import platform

def file_is_modified(drive_file):
    if os.path.exists( drive_file['local_path'] ):
        rtime = time.mktime( time.strptime( drive_file['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ' ) )
        ltime = os.path.getmtime( drive_file['local_path'] )
        return rtime > ltime
    else:
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

def parse_drive_file_metadata(service, drive_file, path):
    remote_path = path + '/' + drive_file['title'].replace( '/', '_' )
    drive_file['path'] = remote_path

    local_path = FLAGS.destination + '/' + username + '/' + remote_path
    drive_file['local_path'] = local_path

    revision_list = retrieve_revisions(service, drive_file['id'])
    revision = str(len(revision_list)) if revision_list else '1'
    drive_file['revision'] = revision
    
    drive_file['category'] = file_type_from_mime(drive_file['mimeType'])

    drive_file['label_key'] = ''.join(sorted([(k[0] if v else ' ') for k, v in drive_file['labels'].items()])).upper()

def print_file_metadata(service, drive_file, path, writer, metadata_names, output_format):
    global items_listed
    parse_drive_file_metadata(service, drive_file, path)
    data = list_from_metadata_names( drive_file, metadata_names )
    if writer:
        writer.writerow( data )
    items_listed += 1
    print( output_format.format( *[str(i) for i in data] ))
    
def download_file_and_metadata(service, drive_file, path, metadata_names, output_format=None):
    global items_updated
    parse_drive_file_metadata(service, drive_file, path)
    if not file_is_modified( drive_file ):
        drive_file['status'] = 'current'
        log( f"not modified: {drive_file['local_path']}" )
    else:
        if download_file( service, drive_file ):
            drive_file['status'] = 'updated'
            items_updated += 1
            save_metadata(drive_file)
        else:
            drive_file['status'] = 'error'
            log( f"ERROR downloading: {drive_file['local_path']}" )
    if output_format:
        data = [ maybe_flatten( drive_file.get(name)) for name in metadata_names ]
        print( output_format.format( *[str(i) for i in data] ))
        output_row = output_format.format( *[str(i) for i in data] )
        print( output_row )
        log( output_row )

def save_metadata(drive_file):
    metadata_directory = FLAGS.destination + '/' + username + '/' + FLAGS.metadata_destination 
    ensure_dir(metadata_directory)
    with open(metadata_directory + drive_file['id'] + '-' + drive_file['title'] + '.json', 'w+') as metadata_file:
        json.dump(drive_file, metadata_file)
    metadata_file.close()

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
        

def walk_folder_metadata( service, http, folder, writer=None, metadata_names=None, base_path='.', depth=0 ):
    output_format = name_list_to_format_string( metadata_names )
    param = {'q': f"'{folder['id']}' in parents" }

    while True:
        try:
            file_list = service.files().list(**param).execute()
        except Exception as e:
            print( f'cautght: {e}' )
            log( f"ERROR: Couldn't get contents of folder {file_list['title']}. Retrying..." )
            continue
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
            ensure_dir( path )
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
                    download_file_and_metadata(service, item, path, metadata_names, output_format)

        for item in filter(is_folder, folder_items):
            walk_folder_metadata( service, http, item, writer, metadata_names, path, depth+1 )
            
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
            drive_file = service.files().get(fileId=row[index_of_id]).execute()
            download_file_and_metadata(service, drive_file, path, metadata_names, output_format)

def download_revision(service, drive_file, revision_id, path):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    file_id = drive_file['id']
    
    try:
        revision = service.revisions().get(fileId=file_id, revisionId=revision_id).execute()
    except errors.HttpError as error:
        print( 'An error occurred: %s' % error )
        
    file_location = path + '/' + "(" + revision['modifiedDate'] + ")" + drive_file['title'].replace( '/', '_' )
    if is_google_doc(drive_file):
        if drive_file['mimeType'] == 'application/vnd.google-apps.document':
            download_url = revision['exportLinks']['application/vnd.oasis.opendocument.text']
        if drive_file['mimeType'] == 'application/vnd.google-apps.presentation':
            download_url = revision['exportLinks']['application/pdf']
        if drive_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            download_url = revision['exportLinks']['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        if drive_file['mimeType'] == 'application/vnd.google-apps.drawing':
            download_url = revision['exportLinks']['image/jpeg']
    else:
        download_url = revision['downloadUrl']
    
    if download_url:
        while True:
            try:
                resp, content = service._http.request(download_url)
            except httplib2.IncompleteRead:   # zero bytes from socket
                log( 'Error while reading file %s. Retrying...' % revision['originalFilename'].replace( '/', '_' ) )
                print( 'Error while reading file %s. Retrying...' % revision['originalFilename'].replace( '/', '_' ) )
                # xxx potential log flood if there is no sleep delay here
                continue
            break

        if resp.status == 200:
            try:
                with open( file_location, 'w+' ) as handle:
                    handle.write( content )
            except:
                log( "Could not open file %s for writing. Please check permissions." % file_location )
                return False
            return True
        else:
            log( 'An error occurred: %s' % resp )
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
        if len(revisions.get('items', [])) > 1:
            return revisions.get('items', [])
        return None    
    except errors.HttpError as error:
        return None


def download_file( service, drive_file ):
    """Download a file's content.

    Args:
      service: Drive API service instance.
      drive_file: Drive File instance.
    
    Returns:
      True if successful, else False.
    """
    
    revision_list = retrieve_revisions(service, drive_file['id'])

    if revision_list != None:
        del revision_list[len(revision_list)-1]
        for item in revision_list:
            download_revision(service, drive_file, item['id'], drive_file['local_path'])
    
    if is_google_doc(drive_file):
        if drive_file['mimeType'] == 'application/vnd.google-apps.document':
            download_url = drive_file['exportLinks']['application/vnd.oasis.opendocument.text']
        if drive_file['mimeType'] == 'application/vnd.google-apps.presentation':
            download_url = drive_file['exportLinks']['application/pdf']
        if drive_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            download_url = drive_file['exportLinks']['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
        if drive_file['mimeType'] == 'application/vnd.google-apps.drawing':
            download_url = drive_file['exportLinks']['image/jpeg']
    else:
        download_url = drive_file['downloadUrl']

    if not download_url:
        return False
    else:
        while True:
            try:
                resp, content = service._http.request(download_url)
            except httplib2.IncompleteRead as e:   # zero bytes from socket
                log( f"Exception {e} while reading {drive_file['local_path']}. Retrying..." )
                # xxx potential log flood if there is no sleep delay here
                continue
            if resp.status == 200:
                try:
                    ensure_dir(dirname( drive_file['local_path']))
                    target = open( drive_file['local_path'], 'wb+' )
                except e:
                    log( f"Cannot open {drive_file['local_path']} for writing: {e}" )
                    return False
                target.write( content )
                m = md5()
                m.update( content )
                drive_file['md5local'] = m.hexdigest()

                return True
            else:
                log( 'An error occurred: %s' % resp )
                return False


def main(argv):
    # Let the flags module process the command-line arguments
    try:
        argv = FLAGS(argv)
    except flags.FlagsError as e:
        print( f'{e}\\nUsage: {argv[0]} ARGS\\n{FLAGS}' )
        sys.exit(1)

    # Set the logging according to the command-line flag
    logging.getLogger().setLevel(getattr(logging, FLAGS.log))

    if FLAGS.config.find('/'):
        ensure_dir(dirname(FLAGS.config))
    if not os.path.exists(FLAGS.config):
        yaml.dump({
            'version': gdrive_version,
            'gdrive': {
                'gdrive_auth': 'config/gdrive_config.json',
                'oauth_id':  'config/gdrive.dat',
                'csv_prefix': './filelist-',
                'metadata': 'createdDate,modifiedDate,id,path,revision,lastModifyingUserName,ownerNames,modifiedByMeDate,lastViewedByMeDate,shared,md5Checksum'
                },
            'csv_title': {
                'app':		'Application',
                'category':	'Category',
                'createdDate':	'Created (UTC)',
                'id':		'File Id',
                'index':	'Index',
                'lastModifyingUserName':	'Modfied by',
                'lastViewedByMeDate': 'User Last View',
                'local_path':	'Local Path',
                'md5Checksum':	'MD5',
                'mimeType':	'MIME Type',
                'modifiedByMeDate':	'User Last Mod',
                'modifiedDate':	'Last Modified (UTC)',
                'ownerNames':	'Owner',
                'path':		'Remote Path',
                'revision':	'Revision',
                'shared':	'Is Shared',
                'time':		'TIME (UTC)',
                'user':		'User',
                'version':	'Version',
                }
            }, io.open(FLAGS.config, 'w', encoding='utf8'), default_flow_style=False, allow_unicode=True)

    config = yaml.safe_load(open(FLAGS.config, 'r'))

    api_credentials_file = config.get('gdrive',{}).get('gdrive_auth')
    metadata_names = (config.get('gdrive',{}).get('metadata')).split(',')

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
        oflags.noauth_local_webserver = FLAGS.no_browser
        credentials = run_flow(FLOW, storage, oflags, http)
    http = credentials.authorize(http)

    service = build("drive", "v2", http=http)
    user_info = get_user_info(service)
    
    global username
    
    if user_info != None:
        username = user_info['user']['emailAddress']
    else:
        username = '???'
    ensure_dir(FLAGS.destination + '/' + username + '/')
    open_logfile()
    output_format = name_list_to_format_string( metadata_names )
    try:
        start_time = datetime.now()
        if FLAGS.list_items:
            print( output_format.format( *[ config.get('csv_title',{}).get(name) for name in metadata_names ]))
            csv_prefix = config.get('gdrive',{}).get('csv_prefix')
            if csv_prefix.find('/'):
                ensure_dir(csv_prefix)
            with open(config.get('gdrive',{}).get('csv_prefix') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ config.get('csv_title').get(name) for name in metadata_names ] )
                start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
                walk_folder_metadata( service, http, start_folder, writer, metadata_names)
                print(f'\n{items_downloaded} files downloaded and {items_updated} updated from {username}')

        elif FLAGS.get_items:
            print('download files')
            print( output_format.format( *[ config.get('csv_title').get(name) for name in metadata_names ]))
            start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            with open(config.get('gdrive',{}).get('csv_prefix') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ config.get('csv_title').get(name) for name in metadata_names ] )
                walk_folder_metadata( service, http, start_folder, writer, metadata_names)
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
    main(sys.argv)
