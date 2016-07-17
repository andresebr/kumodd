#!/usr/bin/python

__author__ = 'andrsebr@gmail.com (Andres Barreto)'

import sys 
import os
import gflags
import ConfigParser
import modules.gdrive as gdrive

FLAGS = gflags.FLAGS

gflags.DEFINE_enum('logging_level', 'ERROR', ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],'Set the level of logging detail.')
gflags.DEFINE_enum('service', None, ['gdrive','dropbox','box','onedrive'], 'Service to use', short_name='s' )
gflags.DEFINE_enum('list_items', None, ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'officedocs', 'image', 'audio', 'video', 'other'], 'List files and directories from the selected service', short_name='l')
gflags.DEFINE_enum('get_items', None, ['all', 'doc', 'xls', 'ppt', 'text', 'pdf', 'officedocs', 'image', 'audio', 'video', 'other'], 'Download files and create directories from the selected service', short_name='d')
gflags.DEFINE_list('usecsv', None, 'Download files from the service using a previously generated csv file', short_name='csv')
gflags.DEFINE_string('destination', 'downloaded/', 'Destination folder location', short_name='p')
gflags.DEFINE_string('metadata_destination', 'metadata/', 'Destination folder for metadata information', short_name='m')
gflags.DEFINE_boolean('debug', False, 'Log folder contents as being fetched' )

def main(argv):
	try:
		argv = FLAGS(argv)
	except gflags.FlagsError, e:
		print '%s\\nUsage: %s ARGS\\n%s' % (e, argv[0], FLAGS)
		sys.exit(1)
		
	if FLAGS.destination == 'downloaded/': 
		if not os.path.exists(FLAGS.destination):
			log( "Creating directory: %s" % directory )
			os.makedirs(FLAGS.destination)
			
	if FLAGS.list_items != None: 
		if not os.path.exists('localdata/'):
			log( "Creating directory: %s" % directory )
			os.makedirs('localdata/')
	
	if FLAGS.service == 'gdrive':
		gflags.DEFINE_string('logfile', 'gdrive.log', 'Location of file to write the log' )
		gflags.DEFINE_string('drive_id', 'root', 'ID of the folder whose contents are to be fetched' )
		gdrive.main(argv)
	elif FLAGS.service == 'dropbox':
		print 'Coming soon...'
	elif FLAGS.service == 'box':
		print 'Coming soon...'
	elif FLAGS.service == 'onedrive':
		print 'Coming soon...'
	else:
		print 'No service selected'
	
if __name__ == '__main__':
	main(sys.argv)
