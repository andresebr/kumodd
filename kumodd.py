#!/usr/bin/env python3
# -*- compile-command: "./kumodd.py -c config/test.cfg -s gdrive -l doc"; -*-
__author__ = 'andrsebr@gmail.com (Andres Barreto), rich.murphey@gmail.com'

from absl import app, flags
import logging
import modules.gdrive as gdrive
import os
import sys 

FLAGS = flags.FLAGS

flags.DEFINE_enum('log', 'ERROR',
                  ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                  'Set the level of logging detail.')
flags.DEFINE_enum('service', 'gdrive',
                  ['gdrive','dropbox','box','onedrive'], 'Service to use', short_name='s' )
flags.DEFINE_enum('list_items', None,
                  ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'office', 'image', 'audio', 'video', 'other'],
                  'List files and directories, optionally filtered by category', short_name='l')
flags.DEFINE_enum('get_items', None,
                  ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'office', 'image', 'audio', 'video', 'other'],
                  'Download files and create directories, optionally filtered by category', short_name='d')
flags.DEFINE_list('usecsv', None,
                  'Download files from the service using a previously generated csv file', short_name='csv')
flags.DEFINE_string('destination', './download', 'Destination folder location', short_name='p')
flags.DEFINE_string('metadata_destination', './download/metadata',
                    'Destination folder for metadata information', short_name='m')

def main(argv):
    try:
        argv = FLAGS(argv)
    except flags.FlagsError as e:
        print( f'{e}\\nUsage: {argv[0]} ARGS\\n{FLAGS}' )
        sys.exit(1)
        
    if not os.path.exists(FLAGS.destination):
        os.makedirs(FLAGS.destination)
            
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
    app.run(main)
