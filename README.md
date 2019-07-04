# kumodd

Kumodd collects files and meta-data from a specified Google Drive account.

It can download files, or generate a CSV file of meta-data.  
Files can be filtered by category, such as doc, image, or video.  
Meta-data columns may be selected in the configuration file.

## Usage examples

To list all documents, use -l:
``` shell
kumodd.py -l doc
Created (UTC)            Last Modified (UTC)      File Id                                       Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z 1BK0I0ScYsZPembZdG9B9qBgtXV5WpyJ3JY31W-9ldo8  My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z 0B7pAT_44h5smSGVkcjywyudk78bs9789sboeuyt2tro  My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z 0B7pAT_44h5sbs897bsmazZorexlchm0wu90sgzrlu9h  My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z 13qAT9ARVaCbGKmCXiN_60XnCAyE5ZrXz_4uKRjaE3mU  My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```
Use -d (download) and -p (path) to save all PDFs to a folder:

    kumodd.py -d pdf -p /home/user/Desktop/

Both the list (-l) and download (-d) options create a CSV file equivalent to the table above. 

The default CSV file name is ./filelist-username.csv. It consists of a prefix specified
in config/config.yml (below), appended by the google drive user name and .csv suffix.

If config/config.yml does not exist, kumodd will create it using:
``` yaml
gdrive:
  gdrive_auth: config/gdrive_config.json
  oauth_id: config/gdrive.dat
  csv_prefix: ./filelist-
  metadata: createdDate,modifiedDate,id,path,revisions,lastModifyingUserName,ownerNames,md5Checksum,modifiedByMeDate,lastViewedByMeDate,shared

```

To select an alternate config file, use -c:

    kumodd.py -c config/alternate.yml

To download all of the files listed in a previously generated CSV file, use -csv:

    kumodd.py -csv ./filelist-username.csv

## Usage

    kumodd.py [-d <filter>] [-l <filter>] [-csv <filename>]

Only one of -d, -l, or -csv should be used.

Option	| Description 
:------	| :-----------
-l filter	| List files. Also create a CSV file list. Filters are described below.
-d filter	| Download files. Also create a CSV file list.
-csv path	| Download files listed in path, a previously generated CSV file.  
-log level | level is either DEBUG, INFO, WARNING, ERROR, or CRITICAL.
-no_browser | Do not open web browser. Instead print the URL.
-m dir | Save meta-data in dir.
-s service	| Select the cloud service.  gdrive is the only supported service.


The filter option limits output to a selected category of files.  A file's category is determined its mime type.

Filter	| Description 
:------	| :-----------
all	| All files stored in the account
doc	| Documents including .doc, .docx, and .odf
xls	| Spreadsheets
ppt	| Presentation files
text	| Text/source code files
pdf	| PDF files
officedocs	| All document, spreadsheet and presentation files
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
## Meta-data

Default meta-data are:

Name	| Description 
------:	| :-----------
createdDate             |  Created Time (UTC)
modifiedDate            |  Last Modified Time (UTC)
id                      |  Unique [Google Drive File ID](https://developers.google.com/drive/api/v3/about-files)
path                    |  Google Drive File Path
revisions               |  Number of revisions
lastModifyingUserName   |  Last Modified by (user name)
ownerNames              |  Owner (user name)
md5Checksum             |  MD5 digest.  Only for file types not native to Google Docs.
modifiedByMeDate        |  Time Last Modified by Account Holder (UTC)
lastViewedByMeDate      |  Time Last Viewed by Account Holder (UTC)
shared                  |  Is shared (true/false)

One can change the meta-data fields.  They are specified by the tag, metadata, in config/config.yml shown above.

Meta-data names are described in the 
[Google Drive API Documentation](https://developers.google.com/drive/api/v3/reference/files).
A few of the available metadata names are shown below. This is the metadata of a Google Doc.

``` javascript
{'alternateLink': 'https://docs.google.com/document/d/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/edit?usp=drivesdk',
 'appDataContents': False,
 'capabilities': {'canCopy': True, 'canEdit': True},
 'copyRequiresWriterPermission': False,
 'copyable': True,
 'createdDate': '2019-06-24T05:04:47.055Z',
 'editable': True,
 'embedLink': 'https://docs.google.com/document/d/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/preview?ouid=118325858994091373100',
 'etag': '"_sqIxUq0fTFLIA71mBDQotbHWsg/TUM2MMT1NgD3NAz5NQ"',
 'explicitlyTrashed': False,
 'exportLinks': {'application/epub+zip': 'https://docs.google.com/feeds/download/documents/export/Export?id=1B0IK0SYcsZePmbdZG99BqBtgXVW5py3JJY31W-l9do8&exportFormat=epub', 'application/pdf': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=pdf', 'application/rtf': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=rtf', 'application/vnd.oasis.opendocument.text': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=odt', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=docx', 'application/zip': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=zip', 'text/html': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=html', 'text/plain': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=txt'},
 'iconLink': 'https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.google-apps.document',
 'id': '1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8',
 'kind': 'drive#file',
 'labels': {'hidden': False, 'restricted': False, 'starred': False, 'trashed': False, 'viewed': True},
 'lastModifyingUser': {'displayName': 'John Doe', 'emailAddress': 'john.doe@gmail.com', 'isAuthenticatedUser': True, 'kind': 'drive#user', 'permissionId': '14466611316174614251', 'picture': {'url': 'https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}},
 'lastModifyingUserName': 'John Doe',
 'lastViewedByMeDate': '2019-06-24T05:41:17.095Z',
 'markedViewedByMeDate': '1970-01-01T00:00:00.000Z',
 'mimeType': 'application/vnd.google-apps.document',
 'modifiedByMeDate': '2019-06-24T05:41:17.095Z',
 'modifiedDate': '2019-06-24T05:41:17.095Z',
 'ownerNames': ['John Doe'],
 'owners': [{'displayName': 'John Doe', 'emailAddress': 'john.doe@gmail.com', 'isAuthenticatedUser': True, 'kind': 'drive#user', 'permissionId': '14466611316174614251', 'picture': {'url': 'https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}}],
 'parents': [{'id': '0AIpnT_44h5smUk9PVA', 'isRoot': True, 'kind': 'drive#parentReference', 'parentLink': 'https://www.googleapis.com/drive/v2/files/0AIpnT_44h5smUk9PVA', 'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/parents/0AIpnT_44h5smUk9PVA'}],
 'quotaBytesUsed': '0',
 'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8',
 'shared': False,
 'spaces': ['drive'],
 'thumbnailLink': 'https://docs.google.com/a/feeds/vt?gd=true&id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&v=5&s=AMedNnoAAAAAXRxA8DRkzkTPYWsf3mzIcWQlHVAxFmMB&sz=s220',
 'title': 'Untitled document',
 'userPermission': {'etag': '"_sqIxUq0fTLFIA17mBQDotbHWsg/zxcSjdx1q8ilez4u1L71gst1zd0"', 'id': 'me', 'kind': 'drive#permission', 'role': 'owner', 'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/permissions/me', 'type': 'user'},
 'version': '12',
 'writersCanShare': True}
```

## Setup

To setup kumodd, install python and git, then install kumodd and requirements, obtain an Oauth ID required for
Google API use, and finally, authorize access to the specified account.

1. Install python 3 and git.

        apt install python3 git

    On windows, make sure they are in the PATH environment
    variable

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
       project](https://console.cloud.google.com/apis/credentials). Or select APIs & Services, then Credentials.
    1. Click "Create Credentials" and select "Oauth client ID".
    1. Select the radio button "Web Application".
    1. In "Authorized redirect URIs", enter: http://localhost:8080
    1. Click "create".  Next, a dialog "OAuth client" will pop up.
    1. Click OK.  Next, it will show a list of "Oauth 2.0 client IDs".
    1. Click the down arrow icon at far right of the new ID.  The ID will download.
    1. Copy the downloaded ID it to kumodd/config/gdrive.json.

1. Authorize kumodd to access the cloud account:

    The first time kumodd is used (e.g. kumodd.py -l all), it will open the
    cloud login page in a web browser.
    1. Login to the cloud account. Next, it will request approval.
    1. Click "Approve". Next, kumodd stores the Oauth token in config/gdrive.dat.  
    
    If there is no local browser, or if -no_browser is used, kumodd will
    instead print a URL of the cloud login page.
    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  Next, it will request approval.
    1. Click "Approve". Next, the page will show an access token.
    1. Copy the token from the web page. Paste it into kumodd, and press enter. Next, kumodd saves the
    Oauth token in config/gdrive.dat.

    Once authorized, the login page will not be shown again unless the token
    (config/gdrive.dat) expires or is deleted.

## Caveats

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

