#!/usr/bin/env python3
# -*- compile-command: "./kumodd.py -c config/test.cfg -s gdrive -l doc"; -*-
__author__ = 'andrsebr@gmail.com (Andres Barreto), rich.murphey@gmail.com'

import sys 
import os
import logging
from absl import flags
import configparser
import modules.gdrive as gdrive

FLAGS = flags.FLAGS

flags.DEFINE_enum('logging_level', 'ERROR', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],'Set the level of logging detail.')
flags.DEFINE_enum('service', None, ['gdrive','dropbox','box','onedrive'], 'Service to use', short_name='s' )
flags.DEFINE_enum('list_items', None, ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'officedocs', 'image', 'audio', 'video', 'other'], 'List files and directories from the selected service', short_name='l')
flags.DEFINE_enum('get_items', None, ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'officedocs', 'image', 'audio', 'video', 'other'], 'Download files and create directories from the selected service', short_name='d')
flags.DEFINE_list('usecsv', None, 'Download files from the service using a previously generated csv file', short_name='csv')
flags.DEFINE_string('destination', 'downloaded/', 'Destination folder location', short_name='p')
flags.DEFINE_string('metadata_destination', 'metadata/', 'Destination folder for metadata information', short_name='m')
flags.DEFINE_boolean('debug', False, 'Log folder contents as being fetched' )

def main(argv):
    try:
        argv = FLAGS(argv)
    except flags.FlagsError as e:
        print( f'{e}\\nUsage: {argv[0]} ARGS\\n{FLAGS}' )
        sys.exit(1)
        
    if FLAGS.destination == 'downloaded/': 
        if not os.path.exists(FLAGS.destination):
            directory = FLAGS.destination
            logging.info( "Creating directory: %s" % directory )
            os.makedirs(FLAGS.destination)
            
    if FLAGS.list_items != None: 
        if not os.path.exists('localdata/'):
            directory = 'localdata/'
            logging.info( "Creating directory: %s" % directory )
            os.makedirs('localdata/')
    
    if FLAGS.service == 'gdrive':
        flags.DEFINE_string('logfile', 'gdrive.log', 'Location of file to write the log' )
        flags.DEFINE_string('drive_id', 'root', 'ID of the folder whose contents are to be fetched' )
        gdrive.main(argv)
    elif FLAGS.service == 'dropbox':
        print( 'Coming soon...' )
    elif FLAGS.service == 'box':
        print( 'Coming soon...' )
    elif FLAGS.service == 'onedrive':
        print( 'Coming soon...' )
    else:
        print( 'No service selected' )
    
if __name__ == '__main__':
    main(sys.argv)
