# kumodd

Kumodd downloads files and/or generates a CSV file of metadata from a specified Google
Drive account in a forensically sound manner.

Files can be filtered by category, such as doc, image, or video.  
metadata columns may be selected in the configuration file.  
The last access and last modify times are preserved and verified. On windows, the create time is.  
The remote and local MD5 digests are verified.

## Usage examples

List (-l) all documents:
``` shell
kumodd.py -l doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

Download (-d) all PDFs to path (-p) /home/user/Desktop/:

    kumodd.py -d pdf -p /home/user/Desktop/

Both the list (-l) and download (-d) options create a CSV file equivalent to the table above. 

Download all of the files listed in a previously generated CSV file:

    kumodd.py -csv ./filelist-username.csv

The default CSV file is ./filelist-username.csv. Set the filename prefix in
config/config.yml. The google user name and .csv suffix are appended.

To download from a CSV file, it must include the 'path' and 'id' metadata.  They are
included in the default metadata.

If config/config.yml does not exist, kumodd will create it using:
``` yaml
gdrive:
  gdrive_auth: config/gdrive_config.json
  oauth_id: config/gdrive.dat
  csv_prefix: ./filelist-
  metadata: createdDate,modifiedDate,id,path,revisions,lastModifyingUserName,ownerNames,md5Checksum,modifiedByMeDate,lastViewedByMeDate,shared

```
Select an alternate config file (-c):

    kumodd.py -c config/alternate.yml

Native Google Apps documents, spreadsheets and presentations are downloaded in LibreOffice format.
The API does not provide a remote MD5 for native Google Apps docs, sheets or slides.
As a result, only the local MD5 digest is reported.

## Usage

    kumodd.py [-d <filter>] [-l <filter>] [-csv <filename>]

Only one of -d, -l, or -csv should be used.

Option		| Description 
------:		| :-----------
-l filter	| List files. Also create a CSV file list. Filters are described below.
-d filter	| Download files. Also create a CSV file list.
-csv path	| Download files listed in path, a previously generated CSV file.  
-log level	| level is either DEBUG, INFO, WARNING, ERROR, or CRITICAL.
-no_browser	| Do not open web browser. Instead print the URL.
-m dir		| Save metadata in dir.
-s service	| Select the cloud service.  gdrive is the only supported service.


The filter option limits output to a selected category of files.  A file's category is determined its mime type.

Filter	| Description 
------:	| :-----------
all	| All files stored in the account
doc	| Documents including .doc, .docx, and .odf
xls	| Spreadsheets
ppt	| Presentation files
text	| Text/source code files
pdf	| PDF files
office	| Document, spreadsheet and presentation files
image	| Image files
audio	| Audio files
video	| Video files

To relay kumodd access though an HTTP proxy, specify the proxy in config/config.yml:
``` yaml
proxy:
  host: proxy.host.com
  port: 8888 (optional)
  user: username (optional)
  pass: password (optional)
```
## Metadata

One can change the metadata fields output by kumodd.  They are specified by the tag,
metadata, in config/config.yml shown above.  The default metadata are:

Name			| Description 
------:			| :-----------
createdDate             | Created Time (UTC)
modifiedDate            | Last Modified Time (UTC)
title			| File name
category		| one of: doc, xls, ppt, text, pdf, image, audio, video or other
size			| size (bytes) of download if new or updated.  Otherwise None.
status			| current, updated, or error if downloading. Otherwise None.
revisions               | Number of revisions
mimeType		| MIME file type
path                    | File path in Google Drive 
id                      | Unique [Google Drive File ID](https://developers.google.com/drive/api/v3/about-files)
lastModifyingUserName   | Last Modified by (user name)
ownerNames              | Owner (user name)
md5Checksum             | MD5 digest of remote file. None if file is a native Google Apps Document.
md5local		| md5 of download if new or updated.  Otherwise None
modifiedByMeDate        | Time Last Modified by Account Holder (UTC)
lastViewedByMeDate      | Time Last Viewed by Account Holder (UTC)
shared                  | Is shared (true/false)

Shown below are a few of the metadata that are derived attributes, computed locally by
kumodd. The names are not found in the data retrieved from google drive, but rather
computed from the data or metadata obtained from google drive.

Name		| Description 
------:		| :-----------
path		| a unix style path of remote file in google drive.
local_path	| path of file in local file system
revisions	| number of revisions of file
md5local	| md5 of download if new or updated.  Otherwise None
size		| size (bytes) of download if new or updated.  Otherwise None.
status		| current, updated, or error if downloading. Otherwise None.


Metadata names obtained from Google Drive are described in the [Google Drive API
Documentation](https://developers.google.com/drive/api/v3/reference/files).  A few of
the available metadata names are shown below. This is the metadata of a PDF file.

``` yaml
alternateLink: https://drive.google.com/a/murphey.org/file/d/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/view?usp=drivesdk
appDataContents: false
capabilities: {canCopy: true, canEdit: true}
category: pdf
copyRequiresWriterPermission: false
copyable: true
createdDate: '2017-09-28T20:06:50.000Z'
downloadUrl: https://doc-0k-9o-docs.googleusercontent.com/docs/securesc/m7lwc9em35jjdnsnezv7rlslwb7hsf02/0b2slbx08rcsbwz9rilnq9rqup99h7nh/1562400000000/14466611316174614883/14466611316174614883/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ?h=07676726225626533888&e=download&gd=true
editable: true
embedLink: https://drive.google.com/a/murphey.org/file/d/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/preview?usp=drivesdk
etag: '"_sblwcq0fTsl4917mBslb2bHWsg/MTUwNjYyOTM4OTA2Mg"'
explicitlyTrashed: false
fileExtension: pdf
fileSize: '2843534'
headRevisionId: 0B4pnT_44h5smaXVvSE9GMUtSMFJjSWVDeXQxTWhCeUFMUW9ZPQ
iconLink: https://drive-thirdparty.googleusercontent.com/16/type/application/pdf
id: 0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ
kind: drive#file
label_key: '     '
labels: {hidden: false, restricted: false, starred: false, trashed: false, viewed: false}
lastModifyingUser:
  displayName: John Doe
  emailAddress: john.doe@gmail.com
  isAuthenticatedUser: true
  kind: drive#user
  permissionId: '14466611316174614251'
  picture: {url: 'https://lh5.googleusercontent.com/-ptNwlcuNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}
lastModifyingUserName: Rich Murphey
local_path: ./download/rich@murphey.org/./My Drive/TxDOT Accident Report (551632).pdf
markedViewedByMeDate: '1970-01-01T00:00:00.000Z'
md5Checksum: 5d5550259da199ca9d426ad90f87e60e
md5Local: 5d5550259da199ca9d426ad90f87e60e
md5Match: match
mimeType: application/pdf
modifiedByMeDate: '2017-09-28T20:09:49.062Z'
modifiedDate: '2017-09-28T20:09:49.062Z'
originalFilename: TxDOT Accident Report (551632).pdf
ownerNames: [Rich Murphey]
owners:
- displayName: Rich Murphey
  emailAddress: rich@murphey.org
  isAuthenticatedUser: true
  kind: drive#user
  permissionId: '14466611316174614251'
  picture: {url: 'https://lh5.googleusercontent.com/-ptNwlcuNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}
parents:
- {id: 0AIpnT_44h5smUk9PVA, isRoot: true, kind: drive#parentReference, parentLink: 'https://www.googleapis.com/drive/v2/files/0AIpnT_44h5smUk9PVA',
  selfLink: 'https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/parents/0AIpnT_44h5smUk9PVA'}
path: ./My Drive/TxDOT Accident Report (551632).pdf
quotaBytesUsed: '2843534'
revision: '1'
selfLink: https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ
shared: false
spaces: [drive]
status: update
title: TxDOT Accident Report (551632).pdf
userPermission: {etag: '"_sblwcq0fTsl4917mBslb2bHWsg/TpnHf_kgQXZabQ7VDW-96dK3owM"',
  id: me, kind: drive#permission, role: owner, selfLink: 'https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/permissions/me',
  type: user}
version: '5'
webContentLink: https://drive.google.com/a/murphey.org/uc?id=0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ&export=download
writersCanShare: true
```

Metadata names are translated to CSV column titles, as shown below in
config/config.yml.  If a title is not defined there, the metadata name is used
as the title.

``` yaml
csv_title:
  app: Application
  category: Category
  createdDate: Created (UTC)
  id: File Id
  index: Index
  lastModifyingUserName: Modified by
  lastViewedByMeDate: User Last View
  local_path: Local Path
  md5Checksum: MD5
  mimeType: MIME Type
  modifiedByMeDate: User Last Mod
  modifiedDate: Last Modified (UTC)
  ownerNames: Owner
  path: Remote Path
  revisions: Revisions
  shared: Is Shared
  time: TIME (UTC)
  user: User
  version: Version
```

The metadata of each file is saved in YAML format under ./metadata.

Note: Kumodd removes the 'thumbnailLink' attribte because 'thumbnailLink' changes each
time the metadata is retrieved from Google Drive, even if nothing else has changed.
Without the 'thumbnailLink' attribute, the metadata should be identical if the file has
not changed in other ways.  This allows comparison of the MD5 digest of the metadata
between newly retrieved and previously retrieved metadata or comparison by 'diff'.

## Setup

To setup kumodd, install python and git, then install kumodd and requirements, obtain an Oauth ID required for
Google API use, and finally, authorize access to the specified account.

1. Install python 3 and git.

        apt install python3 git

    On windows, make sure they are in the PATH environment
    variable.

        SET "PATH=%PATH%;C:\Python37"
        SET "PATH=%PATH%;C:\ProgramFiles\Git\bin"

1. Download kumodd and install the required packages.

    ``` shell
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python3 -m pip install --user -r requirements.txt
    ```

1. Obtain a Google Oauth client ID (required for Google Drive API):

    1. [Create a free google cloud account](
https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account).  
    1. [Login to your Google cloud account](https://console.cloud.google.com).
    1. [Create a Project](https://console.cloud.google.com/projectcreate).
    1. [Create Oauth2 API credential for the
       project](https://console.cloud.google.com/apis/credentials).
    1. Click "Create Credentials" and select "Oauth client ID".
    1. Select the radio button "Web Application".
    1. In "Authorized redirect URIs", enter: http://localhost:8080
    1. Click "create".  Next, a dialog "OAuth client" will pop up.
    1. Click OK.  Next, it will show the list of "Oauth 2.0 client IDs".
    1. Click the down arrow icon at far right of the new ID.  The ID will download.
    1. Copy the downloaded ID it to kumodd/config/gdrive.json.

1. Authorize kumodd to access the cloud account:

    The first time kumodd is used (e.g. kumodd.py -l all), it will open the
    login page in a web browser.
    1. Login to the cloud account. Next, it will request approval.
    1. Click "Approve". Next, kumodd stores the Oauth token in config/gdrive.dat.  
    
    If there is no local browser, or if -no_browser is used, kumodd will
    instead print a URL of the login page.
    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  Next, it will request approval.
    1. Click "Approve". Next, the page will show an access token.
    1. Copy the token from the web page. Paste it into kumodd, and press enter. Next, kumodd saves the
    Oauth token in config/gdrive.dat.

    Once authorized, the login page will not be shown again unless the token
    expires or config/gdrive.dat is deleted.

## Caveats

Google drive allows a folder to contain multiple files with the same name, whereas unix
does not. kumodd downloads only one as it stands. 

Downloading native Google Apps docs, sheets and slides is much slower than non-native
files, due to conversion to LibreOffice formats.

Because native Google Apps files do not provide a MD5 digest, kumod currently only looks
for time stamp differences to detect file changes. It downloads again only when the
local and remote Last Modified time stamps differ by more than one second.

Kumodd looks for multiple revisions of a file, but does not download all of them.

Using an HTTP proxy on Windows does not work due to unresolved issues with httplib2.

[Google rate limits API calls](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas).
At the time of writing, the default rate limits are:

- 1,000,000,000 queries per day
- 1,000 queries per 100 seconds per user
- 10,000 queries per 100 seconds

Kumodd uses the 
[Google API Python Client](https://github.com/googleapis/google-api-python-client) which is officially
supported by Google, and is feature complete and stable.  However, it is not actively
developed.  It has has been replaced by the [Google Cloud client
libraries](https://github.com/googleapis/google-cloud-python) which are in development,
and recommended for new work.

## TODO

For native Google Apps files, kumodd should use the previously saved remote file
metadata to detect whether the file has changed, using for instance, the revision
number.
