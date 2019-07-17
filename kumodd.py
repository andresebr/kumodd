#!/usr/bin/env python3
# -*- compile-command: "./kumodd.py -c config/test.cfg -s gdrive -l doc"; -*-
__author__ = 'andrsebr@gmail.com (Andres Barreto), rich.murphey@gmail.com'

# Copyright (C) 2019  Andres Barreto and Rich Murphey

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

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
flags.DEFINE_enum('list', None,
                  ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'office', 'image', 'audio', 'video', 'other'],
                  'List files in google drive and verify files on disk match MD5', short_name='l')
flags.DEFINE_enum('download', None,
                  ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'office', 'image', 'audio', 'video', 'other'],
                  'Download files, optionally filter, and verify MD5 on disk', short_name='d')
flags.DEFINE_list('usecsv', None,
                  'List files in cloud,  files, optionally filter, and verify MD5 of files on disk', short_name='csv')
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
