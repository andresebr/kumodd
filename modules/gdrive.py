# -*- compile-command: "cd .. ;./kumodd.py -c config/test.cfg -s gdrive -l doc"; -*-
"""Simple command-line sample for the Google Drive API.

Command-line application that retrieves the list of files in google drive.

Usage:
    $ python drive.py

You can also get help on all the command-line flags the program understands
by running:

    $ python drive.py --help

To get detailed log output run:

    $ python drive.py --logging_level=DEBUG
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
from googleapiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError, flow_from_clientsecrets
from oauth2client.tools import run_flow, argparser

#---
from apiclient import errors
import json
from datetime import datetime

OUTPUT_HEADER = ['TIME (UTC)', 'APPLICATION', 'USER', 'FILE ID', 'REMOTE PATH', 'REVISION', 'LOCAL PATH', 'HASH(MD5)', 'MIMETYPE', 'INDEX']
list_template = "{0:4} {1:50} {2:70} {3:10} {4:20}"
log_template = "{:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5} {:>5}"
list_counter = 0
download_counter = 0
update_counter = 0
FLAGS = flags.FLAGS
flags.DEFINE_string('proxy', None, 'URL of web proxy', short_name='q')
flags.DEFINE_boolean('noauth_local_webserver', False, 'disable launching a web browser to authorize access to a google drive account' )
flags.DEFINE_string('config', 'config/config.cfg', 'config file', short_name='c')

config = configparser.ConfigParser()

# The flags module makes defining command-line options easy for
# applications. Run this program with the '--help' argument to see
# all the flags that it understands.


def open_logfile():
    if not re.match( '^/', FLAGS.logfile ):
        FLAGS.logfile = FLAGS.destination + username + '/' + FLAGS.logfile
    global LOG_FILE
    LOG_FILE = open( FLAGS.logfile, 'a' )
    
def log(str):
    LOG_FILE.write( (str + '\n') )

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def is_google_doc(drive_file):
    return True if re.match( '^application/vnd\.google-apps\..+', drive_file['mimeType'] ) else False

def is_file_modified(drive_file, local_file):
    if os.path.exists( local_file ):
        rtime = time.mktime( time.strptime( drive_file['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ' ) )
        ltime = os.path.getmtime( local_file )
        return rtime > ltime
    else:
        return True

def check_file_type(mimetype):
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

def list_items(service, drive_file, dest_path, csv_file):
    global list_counter
    full_path = dest_path + drive_file['title'].replace( '/', '_' )
    remote_path = full_path.replace(FLAGS.destination + username + '/','')
    file_id = drive_file['id']
    revision_list = retrieve_revisions(service, drive_file['id'])
    file_hash = '-'
                
    if revision_list != None:
        revisions = str(len(revision_list))
    else:
        revisions = '1'
                
    if drive_file.get('md5Checksum') != None:
        file_hash = drive_file['md5Checksum']    
        
    output_row = list_template.format(list_counter, file_id, remote_path, revisions, file_hash)
    data = (str(list_counter) + ',' + file_id + ',' + remote_path + ',' + revisions + ',' + file_hash).split(',')
    list_file = csv_file + '-' + username + '.csv'

    with open(list_file, 'a+') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(data)
    list_counter += 1
    return output_row
    
def get_items(service, drive_file, dest_path):
    global update_counter

    full_path = dest_path + drive_file['title'].replace( '/', '_' )
    current_time = datetime.now()
    app_version = 'kumodd-' + config.get('general', 'appversion')
    file_id = drive_file['id']
    remote_path = full_path.replace(FLAGS.destination + username + '/','')
    revision_list = retrieve_revisions(service, drive_file['id'])
    file_hash = '-'
    
    if drive_file.get('md5Checksum') != None:
        file_hash = drive_file['md5Checksum']
    if revision_list != None:
        revisions = 'v.' + str(len(revision_list))
    else:
        revisions = 'v.1'    

    if is_file_modified( drive_file, full_path ):
        is_file_new = not os.path.exists( full_path )
        if download_file( service, drive_file, dest_path ):
            save_metadata(drive_file)
            if is_file_new:
                output_row = log_template.format(str(current_time), app_version, username, file_id, remote_path, revisions, full_path, file_hash)
                print( output_row )
                log(output_row)
            else:
                print( "Updated %s" % full_path )
        else:
            update_counter += 1
            log( "ERROR while saving %s" % full_path )

def save_metadata(drive_file):
    metadata_directory = FLAGS.destination + username + '/' + FLAGS.metadata_destination 
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

def get_folder_contents( service, http, folder, csv_file, base_path='./', depth=0 ):
    result = []
    page_token = None
    flag = True
    
    if FLAGS.debug:
        log( "\n" + '  ' * depth + "Getting contents of folder %s" % folder['title'] )
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
        except:
            print( 'trapped' )
            log( "ERROR: Couldn't get contents of folder %s. Retrying..." % folder['title'] )
            get_folder_contents( service, http, folder, csv_file, base_path, depth )
            return
            
        folder_contents = result
        dest_path = base_path + folder['title'].replace( '/', '_' ) + '/'
    
        def is_file(item):
            return item['mimeType'] != 'application/vnd.google-apps.folder'
    
        def is_folder(item):
            return item['mimeType'] == 'application/vnd.google-apps.folder'
        
        if FLAGS.list_items != None:
            for item in filter(is_file, folder_contents):
                mimetype = item['mimeType']
                
                if FLAGS.list_items == 'doc' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'xls' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'ppt' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'text' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'pdf' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if (FLAGS.list_items == 'officedocs') and (check_file_type(mimetype) == 'doc' or check_file_type(mimetype) == 'xls' or check_file_type(mimetype) == 'ppt'):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'image' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'audio' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'video' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'other' and FLAGS.list_items == check_file_type(mimetype):
                    print( list_items(service, item, dest_path, csv_file) )
                if FLAGS.list_items == 'all':
                    print( list_items(service, item, dest_path, csv_file) )
                
        if FLAGS.get_items != None:    
            ensure_dir( dest_path )
            for item in filter(is_file, folder_contents):

                mimetype = item['mimeType']
                
                if FLAGS.get_items == 'doc' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'xls' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'ppt' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'text' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'pdf' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if (FLAGS.get_items == 'officedocs') and (check_file_type(mimetype) == 'doc' or check_file_type(mimetype) == 'xls' or check_file_type(mimetype) == 'ppt'):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'image' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'audio' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'video' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'other' and FLAGS.get_items == check_file_type(mimetype):
                    get_items(service, item, dest_path, csv_file)
                if FLAGS.get_items == 'all':
                    get_items(service, item, dest_path, csv_file)
    
        for item in filter(is_folder, folder_contents):
            get_folder_contents( service, http, item, csv_file, dest_path, depth+1 )
            
def get_csv_contents(service, http, csv_file, base_path='./'):
    """Print information about the specified revision.

    Args:
        service: Drive API service instance.
        file_id: ID of the file to print revision for.
        revision_id: ID of the revision to print.
    """
    ensure_dir( base_path )
    index_list = FLAGS.usecsv
    csv_file = csv_file + '-' + username + '.csv'

    #TODO: Validate everything!!!
    if index_list[0] == 'all':
        f= open(csv_file, 'rt')
        try:
            reader = csv.reader(f)
            for row in reader:
                path = row[2].split('/')
                del path[len(path)-1]
                remote_path = '/'.join(path)
                dest_path = base_path + remote_path + '/'
                ensure_dir( dest_path )
                item = service.files().get(fileId=row[1]).execute()
                get_items(service, item, dest_path, csv_file)
        finally:
            f.close()
    
    if index_list[0] != 'all':
        for item in index_list:
            if (item.isdigit() or item == 0) and int(item) >= 0:
                f= open(csv_file, 'rt')
                try:
                    reader = csv.reader(f)
                    for row in reader:
                        if item == row[0]:
                            path = row[2].split('/')
                            del path[len(path)-1]
                            remote_path = '/'.join(path)
                            dest_path = base_path + remote_path + '/'
                            ensure_dir( dest_path )
                            item = service.files().get(fileId=row[1]).execute()
                            get_items(service, item, dest_path, csv_file)
                finally:
                    f.close()
            else:    
                print( 'ERROR! Incorrect index: ' + item + ' type all to download <all> files listed in the csv file' )
        
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


def download_file( service, drive_file, dest_path ):
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
            download_revision(service, drive_file, item['id'], dest_path)
    
    file_location = dest_path + drive_file['title'].replace( '/', '_' )
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
            log( 'Error while reading file %s. Retrying...' % drive_file['title'].replace( '/', '_' ) )
            download_file( service, drive_file, dest_path )
            return False
        if resp.status == 200:
            try:
                target = open( file_location, 'w+' )
            except:
                log( "Could not open file %s for writing. Please check permissions." % file_location )
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
    logging.getLogger().setLevel(getattr(logging, FLAGS.logging_level))

    config.read(FLAGS.config)
    tokenfile = config.get('gdrive', 'tokenfile')
    open(tokenfile, 'a').close() # create token file if it does not exist
    csv_file = config.get('gdrive', 'csvfile')
    # api_credentials_file, name of a file containing the OAuth 2.0 information for this
    # application, including client_id and client_secret, which are found
    # on the API Access tab on the Google APIs
    # Console <http://code.google.com/apis/console>
    #api_credentials_file = 'config/client_secrets.json'
    api_credentials_file = config.get('gdrive', 'configurationfile')

    # Set up a Flow object to be used if we need to authenticate.
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

    if config.get('proxy', 'host', fallback=False):
        proxy = config['proxy']
        http = httplib2.Http(
            proxy_info = httplib2.ProxyInfo(
                socks.PROXY_TYPE_HTTP,
		proxy.get('host'), int(proxy.get('port')) ))
    else:
        http = httplib2.Http()

    resp, content = http.request("http://google.com", "GET")

    # If the Credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    try:
        storage = Storage(tokenfile)
        credentials = storage.get()
    except:
        open(tokenfile, "a+").close()     # ensure tokenfile exists
        storage = Storage(tokenfile)
        credentials = None

    if credentials is None or credentials.invalid:
        oflags = argparser.parse_args([])
        oflags.noauth_local_webserver = FLAGS.noauth_local_webserver
        credentials = run_flow(FLOW, storage, oflags, http)

    http = credentials.authorize(http)

    service = build("drive", "v2", http=http)
    user_info = get_user_info(service)
    
    global username
    
    if user_info != None:
        username = user_info['user']['emailAddress']
    else:
        username = '???'
    ensure_dir(FLAGS.destination + username + '/')
    open_logfile()
    
    try:
        start_time = datetime.now()
        print( "Working..." )
        
        if FLAGS.list_items:
            list_file = csv_file + '-' + username + '.csv'
            reset_file(list_file)
            header = list_template.format(OUTPUT_HEADER[9], OUTPUT_HEADER[3], OUTPUT_HEADER[4], OUTPUT_HEADER[5], OUTPUT_HEADER[7])
            print( header )
            start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            get_folder_contents( service, http, start_folder, csv_file, FLAGS.destination + username + '/')
            print('\n' + str(list_counter) + ' files found in ' + username + ' drive')
        
        elif FLAGS.get_items:
            header = log_template.format(OUTPUT_HEADER[0], OUTPUT_HEADER[1], OUTPUT_HEADER[2], OUTPUT_HEADER[3], OUTPUT_HEADER[4], OUTPUT_HEADER[5], OUTPUT_HEADER[6], OUTPUT_HEADER[7])
            print( header )
            start_folder = service.files().get( fileId=FLAGS.drive_id ).execute()
            get_folder_contents( service, http, start_folder, csv_file, FLAGS.destination + username + '/')
            print('\n' + str(download_counter) + ' files downloaded and ' + str(update_counter) + ' updated from ' + username + ' drive')
        
        elif FLAGS.usecsv:
            header = log_template.format(OUTPUT_HEADER[0], OUTPUT_HEADER[1], OUTPUT_HEADER[2], OUTPUT_HEADER[3], OUTPUT_HEADER[4], OUTPUT_HEADER[5], OUTPUT_HEADER[6], OUTPUT_HEADER[7])
            print( header )
            get_csv_contents(service, http, FLAGS.destination + username + '/')
            print('\n' + str(download_counter) + ' files downloaded and ' + str(update_counter) + ' updated from ' + username + ' drive')
        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))
    except AccessTokenRefreshError:
        print ("The credentials have been revoked or expired, please re-run"
        "the application to re-authorize")

if __name__ == '__main__':
    main(sys.argv)
