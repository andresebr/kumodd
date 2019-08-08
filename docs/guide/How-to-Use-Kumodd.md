# How to Use Kumodd

Kumodd is a command line utility. To run Kumodd, open a shell window (eg. CMD or
powershell on Windows, or xterm on linux) and invoke kit with command line options to
specify what action to take.

## List all documents

To list all documents (google doc, .doc, .docx, .odt etc), use:
``` shell
kumodd -list doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

## Filter files by category

To limits files to a selected category, use one of the filters below.  A file's category
is determined its mime type.

Filter	| Description 
:------	| :-----------
all	| All files stored in the account
doc	| Documents: Google Docs, doc, docx, odt
xls	| Spreadsheets: Google Sheets, xls, xlsx, ods
ppt	| Presentations: Google Slides, ppt, pptx, odp
text	| Text/source code files
pdf	| PDF files
office	| Documents, spreadsheets and presentations
image	| Image files
audio	| Audio files
video	| Video files

## Download Files

Download all documents to ./download (the default location):

    kumodd -download doc

Download all PDF files to the path /home/user/Desktop/:

    kumodd -download pdf -path /home/user/Desktop/

To download all of the files listed in a previously generated CSV file, use:

    kumodd -csv ./filelist-username.csv

To verify the files' MD5, size, Last Modified, and Last Accessed time, and MD5 of
metadata, use:

    kumodd -verify -col verify

## How to Export Google Apps Files

Native Google Apps files, such as docs, sheets, slides and drawings, must be converted
upon download. The default conversion format is PDF.  To instead download them in
LibreOffice format, use __-convert opendocument__.  To download them in MS
Office format, use __-convert officedocument__.  Other valid conversion formats
include epub, rtf, zip, html, and plain (.txt).

Download<br/>Conversion<br/>Option			| Google<br/>Docs<br/>as | Google<br/>Sheets<br/>as | Google<br/>Slides<br/>as | Google<br/>Drawings<br/>as
:------			| :-----------	  | :-----------  | :----------- | :-----------
-convert pdf		| .pdf	| .pdf	| .pdf	| .pdf
-convert opendocument	| .odt	| .ods	| .odp	| .odg
-convert officedocument	| .docx	| .xlsx	| .pptx	| .pdf
-convert epub		| .epub	| .pdf	| .pdf	| .pdf
-convert rtf		| .rtf	| .pdf	| .pdf	| .pdf
-convert html		| .html	| .pdf	| .pdf	| .pdf
-convert plain		| .txt 	| .pdf	| .txt	| .pdf

The -convert option also accepts mime types.  For a list of valid mime types for any
given file, look in the keys of the exportLinks value in the file's metadata, shown
below. For this file, -convert application/epub+zip is a valid option.

Sample of mime types for a Google Doc:
``` yaml
exportLinks: {application/epub+zip: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=epub',
  application/pdf: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=pdf',
  application/rtf: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=rtf',
  application/vnd.oasis.opendocument.text: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=odt',
  application/vnd.openxmlformats-officedocument.wordprocessingml.document: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=docx',
  application/zip: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=zip',
  text/html: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=html',
  text/plain: 'https://docs.google.com/feeds/download/documents/export/Export?id=1ut6_Od8NcNo1Lh-QOgNmMZxvbsK14sMnoo&exportFormat=txt'}
```

## Completeness

Google Drive folders can hold multiple files with the same name, differing by their
version number. The trash may hold additional files having the same name, and different
version numbers.  When the version number is greater than 1, \_(v*VERSION*) is appended
before the file extension, such as filename\_(v8).doc.

By default, every available revision is downloaded unless --norevisions is specified, in
which case only the current file (latest revision) is downloaded.  Previous
revisions are saved as filename\_(r*REVISION ID*\_*LAST MODIFIED DATE*).

Results include files in the trash. Files from the trash have the metadata attribute
__trashed == true__.

Results will include malware or other abusive files if present. Kumodd does this by
setting __acknowledgeAbuse=true__ when downloading them files from Google Drive.

Results will include files in Team drives and Shared drives.

Results exclude certain native types such as google maps that are not exportable, and
cannot be downloaded.

By default, results will not include Google Photos or hidden android application data.
To obtain them, use the scope and space options, discussed below.

## Spaces

The default space __drive__.  Use the __--spaces__ option to select a comma-separated list
of spaces to query within the corpus. Supported values are __drive__, __appDataFolder__ and
__photos__.  If photos or appDataFolder are selected, they may require a different scope
and may require different API credentials and different Google Drive account
credentials.

## Scope
    
The default scope is https://www.googleapis.com/auth/drive.readonly.  This provides read
only access to all files and metadata in the user's 'My Drive' folder. This excludes the
Application Data folder.  For a description of the various scopes, including for photos
and app data, see https://developers.google.com/drive/api/v3/about-auth.

## Corpus

The default corpus is __user__. Select a different corpus using the __--corpera__ option.
    
Valid corpera options include:

* __user__: includes all files in "My Drive" and "Shared with me".  
* __domain__: includes all files shared to the user's domain that are searchable.  
* __drive__: includes all files contained in a single shared drive.  
* __allDrives__: includes all files in shared drives that the user is a member of and all files in "My Drive" and "Shared with me." Use of the allSharedDrives corpus is discouraged for efficiency reasons. Use 'drive' or 'user' for efficiency.  

