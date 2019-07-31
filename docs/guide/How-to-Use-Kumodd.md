# How to Use Kumodd

Kumodd is a command line utility. To run Kumodd, open a shell window (eg. CMD or
powershell on Windows, or xterm on linux) and invoke it with command line options to
specify what action to take.

## List all documents

To list all documents (google doc, .doc, .docx, .odt etc), use:
``` shell
kumodd -l doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

## Filter files by category

The filter option limits output to a selected category of files.  A file's category is
determined its mime type.

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

Download (-d) all documents to ./download (the default location):

    kumodd -d doc

Download (-d) all PDF files to path (-p) /home/user/Desktop/:

    kumodd -d pdf -p /home/user/Desktop/

To download all of the files listed in a previously generated CSV file, use:

    kumodd -csv ./filelist-username.csv

To verify the files' MD5, size, Last Modified, and Last Accessed time, and MD5 of
metadata, use:

    kumodd -verify -col verify

## Export Google Apps Files

The default conversion format is PDF.  Native Google Apps files, such as docs, sheets,
slides and drawings, must be converted upon download.  To download them in LibreOffice
format, use the '-convert opendocument' option.  To download them in MS Office format,
use the '-convert officedocument' option.  Other valid conversion formats include epub,
rtf, zip, html, and plain (.txt).

Option			| Google<br/>Docs | Google<br/>Sheets | Google<br/>Slides | Google<br/>Drawings
:------			| :-----------	  | :-----------  | :----------- | :-----------
-convert pdf		| .pdf	| .pdf	| .pdf	| .pdf
-convert opendocument	| .odt	| .ods	| .odp	| .odg
-convert officedocument	| .docx	| .xlsx	| .pptx	| .pdf
-convert epub		| .epub	| .pdf	| .pdf	| .pdf
-convert rtf		| .rtf	| .pdf	| .pdf	| .pdf
-convert html		| .html	| .pdf	| .pdf	| .pdf
-convert plain		| .txt 	| .pdf	| .txt	| .pdf

The -convert option also supports mime types.  For a list of mime types for any given
file, look in the keys of the exportLinks value in the file's metadata.

## Completeness

By default, every available revision is downloaded unless --norevisions is specified, in
which case only the current file (latest revision) is downloaded.  Previous
revisions are saved as filename_(r\<revision id\>_\<last modified date\>).

Results include files in the trash. Files from the trash have the metadata attribute,
labels.trashed == true.

Results will include malware or other abusive files if present. Kumodd does this by
setting acknowledgeAbuse=true when downloading files from Google Drive.

Results will include files in Team drives and Shared drives.

Results exclude certain native types such as google maps that are not exportable, and
cannot be downloaded.

Results will not include Google Photos or application data.  To obtain them, see [Scope
in How to Search for Files](../../Search-Query/#scope).
