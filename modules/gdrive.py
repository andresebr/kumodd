# -*- compile-command: "cd .. ;./kumodd.py -c config/test.cfg -s gdrive -l doc"; -*-
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
import pprint
import sys
import re
import time
import configparser
import csv
import socket
import platform
from collections import Iterable
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
from oauth2client.tools import run_flow, argparser

#---
from apiclient import errors
import json
from datetime import datetime

NAME_TO_TITLE = {
    'createdDate':	'Created (UTC)',
    'modifiedDate':	'Last Modified (UTC)',
    'time':		'TIME (UTC)',
    'version':		'Code/Config Ver',
    'app':		'Application',
    'user':		'User',
    'id':		'File Id',
    'path':		'Remote Path',
    'revisions':	'Revisions',
    'local_path':	'Local Path',
    'md5Checksum':	'MD5',
    'mime':		'MIME Type',
    'index':		'Index',
    'lastModifyingUserName':	'Last Mod by',
    'ownerNames':	'Owner',
    'modifiedByMeDate':	'Last Mod By Me',
    'lastViewedByMeDate': 'Last View By Me',
    'shared':		'Is Shared',
    'version':		'Version',
    }

def name_list_to_format_string( names ):
    """generate a format string for a given list of metadata names"""
    fields = []
    for i, name in enumerate(names):
        if 'path' in name:
            fields.append(f'{{{i}:70}}')
        elif name in ['id']:
            fields.append(f'{{{i}:44}}')
        elif name in ['md5']:
            fields.append(f'{{{i}:32}}')
        elif 'Date' in name or name in ['time']:
            fields.append(f'{{{i}:24}}')
        elif name in ['revision', 'version']:
            fields.append(f'{{{i}:8}}')
        else:
            fields.append(f'{{{i}:20}}')
    return ' '.join( fields )

list_counter = 0
download_counter = 0
update_counter = 0
FLAGS = flags.FLAGS
flags.DEFINE_string('proxy', None, 'URL of web proxy', short_name='q')
flags.DEFINE_boolean('no_browser', False, 'disable launching a web browser to authorize access to a google drive account' )
flags.DEFINE_string('config', 'config/config.cfg', 'config file', short_name='c')

gdrive_version = "1.0"
config = configparser.ConfigParser({
    'general': {'appversion': gdrive_version},
    'proxy': {},
    'gdrive': {
        'configurationfile': 'config/gdrive_config.json',
        'tokenfile':  'config/gdrive.dat',
        'csvfile': 'localdata/gdrivelist',
        'metadata': 'createdDate,modifiedDate,id,path,revisions,lastModifyingUserName,ownerNames,md5Checksum,modifiedByMeDate,lastViewedByMeDate,shared'
     }
    })


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

def parse_drive_file_metadata(service, drive_file, dest_path):
    full_path = dest_path + drive_file['title'].replace( '/', '_' )
    drive_file['local_path'] = full_path

    remote_path = full_path.replace(FLAGS.destination + '/' + username + '/','')
    drive_file['path'] = remote_path

    revision_list = retrieve_revisions(service, drive_file['id'])
    revisions = str(len(revision_list)) if revision_list else '1'
    drive_file['revisions'] = revisions
    
def list_items(service, drive_file, dest_path, writer, metadata_names):
    # print(f"metadata: {drive_file['title']}")
    # pprint.pprint(drive_file)
    global list_counter
    parse_drive_file_metadata(service, drive_file, dest_path)
    # pprint.pprint(drive_file)
    data = [ maybe_flatten( drive_file.get(name)) for name in metadata_names ]
    if writer:
        writer.writerow( data )
    # pprint.pprint(metadata_names)
    # pprint.pprint(data)
    list_counter += 1
    return list_template.format( *data )
    
def get_items(service, drive_file, dest_path, metadata_names):
    global update_counter
    parse_drive_file_metadata(service, drive_file, dest_path)
    if not file_is_modified( drive_file ):
        log( f"not modified: {drive_file['local_path']}" )
        status = 'current: '
    else:
        if not download_file( service, drive_file ):
            log( f"ERROR downloading: {drive_file['local_path']}" )
            status = 'error:   '
        else:
            status = 'updated: '
            update_counter += 1
            save_metadata(drive_file)
    data = [ maybe_flatten( drive_file.get(name)) for name in metadata_names ]
    output_row = log_template.format( *data )
    print( status, output_row )
    log( status + output_row)

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

def walk_folder_contents( service, http, folder, writer=None, metadata_names=None, base_path='./', depth=0 ):
    result = []
    page_token = None
    flag = True
    
    while flag:
        
        try:
            param = {}
            param['q'] = "'" + folder['id'] + "'" + " in parents"
            if page_token:
                param['pageToken'] = page_token
            folder_contents = service.files().list(**param).execute()
            result.extend(folder_contents['items'])
            page_token = folder_contents.get('nextPageToken')
            
            if not page_token:
                flag = False
        except Exception as e:
            print( f'cauthgt: {e}' )
            log( f"ERROR: Couldn't get contents of folder {folder['title']}. Retrying..." )
            walk_folder_contents( service, http, folder, writer, metadata_names, base_path, depth )
            return
            
        folder_contents = result
        dest_path = base_path + folder['title'].replace( '/', '_' ) + '/'
    
        def is_file(item):
            return item['mimeType'] != 'application/vnd.google-apps.folder'
    
        def is_folder(item):
            return item['mimeType'] == 'application/vnd.google-apps.folder'
        
        if FLAGS.list_items != None:
            for item in filter(is_file, folder_contents):
                if ( FLAGS.list_items == 'all' ):
                    print( list_items(service, item, dest_path, writer, metadata_names) )

                elif ( FLAGS.list_items in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other']
                    and FLAGS.list_items == file_type_from_mime(item['mimeType']) ):
                    print( list_items(service, item, dest_path, writer, metadata_names) )

                elif ( FLAGS.list_items == 'officedocs'
                      and file_type_from_mime(item['mimeType']) in ['doc', 'xls', 'ppt']):
                    print( list_items(service, item, dest_path, writer, metadata_names) )

        if FLAGS.get_items != None:    
            ensure_dir( dest_path )
            for item in filter(is_file, folder_contents):
                if ( FLAGS.get_items == 'all' ):
                    get_items(service, item, dest_path, metadata_names)

                elif ( ( FLAGS.get_items in ['doc','xls', 'ppt', 'text', 'pdf', 'image', 'audio', 'video', 'other'] )
                      and FLAGS.get_items == file_type_from_mime(item['mimeType']) ):
                    get_items(service, item, dest_path, metadata_names)

                elif ( FLAGS.get_items == 'officedocs'
                      and file_type_from_mime(item['mimeType']) in ['doc', 'xls', 'ppt']):
                    get_items(service, item, dest_path, metadata_names)
                # else:
                #     print( f"skipped: {FLAGS.get_items} {file_type_from_mime(item['mimeType'])} {item['title']} " )

        for item in filter(is_folder, folder_contents):
            walk_folder_contents( service, http, item, writer, metadata_names, dest_path, depth+1 )
            
def get_csv_contents(service, http, csv_file, metadata_names=None, base_path='./'):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    ensure_dir( base_path )
    with open(FLAGS.usecsv[0], 'rt') as csv_handle:
        reader = csv.reader(csv_handle)
        header = next(reader, None)
        index_of_path = header.index(NAME_TO_TITLE['path'])
        index_of_id = header.index(NAME_TO_TITLE['id'])
        for row in reader:
            path = row[index_of_path].split('/')
            del path[len(path)-1]
            remote_path = '/'.join(path)
            dest_path = base_path + remote_path + '/'
            ensure_dir( dest_path )
            item = service.files().get(fileId=row[index_of_id]).execute()
            get_items(service, item, dest_path, metadata_names)

def download_revision(service, drive_file, revision_id, dest_path):
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
        
    file_location = dest_path + "(" + revision['modifiedDate'] + ")" + drive_file['title'].replace( '/', '_' )
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
        try:
            resp, content = service._http.request(download_url)
        except httplib2.IncompleteRead:
            log( 'Error while reading file %s. Retrying...' % revision['originalFilename'].replace( '/', '_' ) )
            download_revision( service, file_id, revision_id, dest_path )
            return False
        if resp.status == 200:
            try:
                target = open( file_location, 'w+' )
            except:
                log( "Could not open file %s for writing. Please check permissions." % file_location )
                return False
            target.write( content )
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
      File's content if successful, None otherwise.
    """
    global download_counter
    
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
    if download_url:
        try:
            resp, content = service._http.request(download_url)
        except httplib2.IncompleteRead:
            log( f"Error while reading file {drive_file['local_path']}. Retrying..." )
            download_file( service, drive_file, drive_file['local_path'] )
            return False
        if resp.status == 200:
            try:
                target = open( drive_file['local_path'], 'wb+' )
            except:
                log( f"Could not open file {drive_file['local_path']} for writing. Please check permissions." )
                return False
            target.write( content )
            download_counter += 1
            return True
        else:
            log( 'An error occurred: %s' % resp )
            return False
    else:
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

    config.read(FLAGS.config)
    try: 
        metadata_names = config.get('gdrive', 'metadata').split(',')
    except:
        metadata_names = 'createdDate,modifiedDate,id,path,revisions,lastModifyingUserName,ownerNames,md5Checksum,modifiedByMeDate,lastViewedByMeDate,shared'.split(',')

    api_credentials_file = config.get('gdrive', 'configurationfile')

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

    if 'proxy' in config and 'host' in config['proxy']:
        proxy = config['proxy']
        try:
            proxy_uri = 'http://' + proxy.get('host')
            if 'port' in proxy:
                proxy_uri += ':' + proxy.get('port')
            resp, content = http.request(proxy_uri, "GET")
        except Exception as e:
            print(f"\nCannot connect to proxy at: {proxy_uri}.  Please check your network.\n\n")

        http = httplib2.Http(
            disable_ssl_certificate_validation=True,
            proxy_info = httplib2.ProxyInfo(
                httplib2.socks.PROXY_TYPE_HTTP,
                proxy_host = proxy.get('host'),
                proxy_port = int(proxy.get('port')) if proxy.get('port') else None,
                proxy_user = proxy.get('user', fallback=None),
                proxy_pass = proxy.get('pass', fallback=None) ))
    else:
        http = httplib2.Http()

    try:
        resp, content = http.request("http://google.com", "GET")
    except Exception as e:
        print(f"""\nCannot connect to google.com.  Please check your network.

Error: {e}\n""" )
        sys.exit(1)

    # If the Credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    tokenfile = config.get('gdrive', 'tokenfile')
    try:
        storage = Storage(tokenfile)
        credentials = storage.get()
    except:
        open(tokenfile, "a+").close()     # ensure tokenfile exists
        storage = Storage(tokenfile)
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
    
    
    global list_template, log_template
        
    try:
        start_time = datetime.now()
        if FLAGS.list_items:
            list_template = name_list_to_format_string( metadata_names )
            header = list_template.format( *[ NAME_TO_TITLE[name] for name in metadata_names ])
            print( header )
            start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            with open(config.get('gdrive', 'csvfile') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ NAME_TO_TITLE[name] for name in metadata_names ] )
                walk_folder_contents( service, http, start_folder, writer, metadata_names, FLAGS.destination + '/' + username + '/')
                print('\n' + str(list_counter) + ' files found in ' + username + ' drive')
        
        elif FLAGS.get_items:
            log_template = name_list_to_format_string( metadata_names )
            header = log_template.format( *[ NAME_TO_TITLE[name] for name in metadata_names ])
            print( 'Status   ', header )
            start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            with open(config.get('gdrive', 'csvfile') + username + '.csv', 'w') as csv_handle:
                writer = csv.writer(csv_handle, delimiter=',')
                writer.writerow( [ NAME_TO_TITLE[name] for name in metadata_names ] )
                walk_folder_contents( service, http, start_folder, writer, metadata_names, FLAGS.destination + '/' + username + '/')
                print('\n' + str(download_counter) + ' files downloaded and ' + str(update_counter) + ' updated from ' + username + ' drive')

        elif FLAGS.usecsv:
            log_template = name_list_to_format_string( metadata_names )
            header = log_template.format( *[ NAME_TO_TITLE[name] for name in metadata_names ])
            print( 'Status   ', header )
            get_csv_contents(service, http, FLAGS.usecsv[0], metadata_names, FLAGS.destination + '/' + username + '/')
            print('\n' + str(download_counter) + ' files downloaded and ' + str(update_counter) + ' updated from ' + username + ' drive')

        end_time = datetime.now()
        print(f'Duration: {end_time - start_time}')
    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run the application to re-authorize")

if __name__ == '__main__':
    main(sys.argv)
