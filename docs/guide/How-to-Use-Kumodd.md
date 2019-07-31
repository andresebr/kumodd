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

By default, native Google Apps files (docs, sheets and slides) are downloaded in PDF
format. To instead download them in LibreOffice format, use the '--nopdf' option.

By default, every available revision is downloaded unless --norevisions is specified, in
which case only the current file (latest revision) is downloaded.  Previous
revisions are saved as filename_(revision id_last modified date).

To download all of the files listed in a previously generated CSV file, use:

    kumodd -csv ./filelist-username.csv

To verify the files' MD5, size, Last Modified, and Last Accessed time, and MD5 of
metadata, use:

    kumodd -verify -col verify
