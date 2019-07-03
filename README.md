# kumodd

Kumodd collects data from a specified Google Drive account.

Optional filters limit by file cateories, such as doc, image, or video.  
Output can include file contents or only a table of meta-data.  
Columns may be selected in the configuration file.

``` shell
./kumodd.py -l doc
Created (UTC)            Last Modified (UTC)      File Id                                       Remote Path                   Revision   Last Modified by Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z 1BK0I0ScYsZPembZdG9B9qBgtXV5WpyJ3JY31W-9ldo8  My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z 0B7pAT_44h5smSGVkcjywyudk78bs9789sboeuyt2tro  My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z 0B7pAT_44h5sbs897bsmazZorexlchm0wu90sgzrlu9h  My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z 13qAT9ARVaCbGKmCXiN_60XnCAyE5ZrXz_4uKRjaE3mU  My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

## Setup

To setup kumodd, 1) install kumodd and requirements, 2) obtain a Google Oauth
client ID, and 3) authorize access to a specified cloud account.

1. Download kumodd and install the required packages.
    ```
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python3 -m pip install --user -r requirements.txt
    ```

1. Obtain a Google Oauth client ID:
    1. If you do not have a free google cloud account, create one as described in [Create a new billing account](
https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account).  
    1. Login to your [Google cloud account](https://console.cloud.google.com)
    1. Create a project: [Create Project](https://console.cloud.google.com/projectcreate).
    1. Create your Oauth2 API credentials. Select APIs & Services, then Credentials, or go to: [Credentials](https://console.cloud.google.com/apis/credentials).
    1. Click "Create Credentials" and select "Oauth client ID".
    1. Select the radio button "Web Application".
    1. In "Authorized redirect URIs", enter: `http://localhost:8080`
    1. Click "create".  A dialog "OAuth client" will pop up.  Click OK.
    1.  Under "Oauth 2.0 client IDs", to the far right of the new ID, is a down arrow icon. Click the down arrow icon to download it.
    1. Rename it to gdrive.json, and move it to the config directory inside
       the kumodd directory created in step 1: kumodd/config/gdrive.json.

1. Authorize kumodd to access the cloud account:

    When kumodd is used for the first time to connect to a cloud service:
    ```
    python3 kumodd.py -l all
    ```

    Kumodd will open a web browser to the login page of the cloud service (e.g. google
    drive). 
    1. Login to the cloud account. After logging in, the page will request approval for the web service to access the cloud account.  
    1. Approve the access. Then, kumodd stores the access credentials in the config directory.  
    
    If there is no local browser, kumod will instead print a URL for the login page of
    the cloud service. 
    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  It will ask for approval of the web app.
    1. Click "Approve". After clicking approve, the web page will show an access token.  Kumodd will be waiting for input. 
    1. Copy and paste that token into kumodd and press enter. Kumod then saves the
    token in config/gdrive.dat, for later use.

    Once this is done, kumodd will not prompt again for the Google Drive login details unless the token expires or the config/gdrive.dat is deleted.

    To force kumodd to print the URL, and not open local web browser, invoke it with the `--no_browser` option:
    ```
    python3 kumodd.py --no_browser -l all
    ```

## Usage

`python3 kumodd.py [-d <filter>] [-l <filter>] [-csv <filename>]`

Only one of -d, -l, or -csv should be used.

Option	| Description 
:------	| :-----------
-l filter	| List files. Also create a CSV file list.
-d filter	| Download files. Also create a CSV file list.
-csv file	| Download files listed in previously generated CSV file, <file>.
-log level | level is either DEBUG, INFO, WARNING, ERROR, or CRITICAL.
-no_browser | Do not open web browser. Instead print the URL.
-m dir | Save meta-data in dir.
-proxy URL | Send HTTP requests through proxy at URL.
-s service	| Select the cloud service.  gdrive is the only supported service.


The filter option limits output to a selected category of files.  In google drive, file
catetory is determined by the mimetime.

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


## Usage examples

List all files stored in a Google Drive account:

`python3 kumodd.py -l all`

List only images stored in Google Drive:

`python3 kumodd.py -l image`

Download all PDF files and save them in the Desktop folder:

`python3 kumodd.py -d pdf -p /home/user/Desktop/`

The -l and -d options create a CSV file. 
The CSV filen prefix is specified in config/config.cfg. 
``` shell
[gdrive]
csvfile = localdata/gdrivelist
```

The account name and .csv are appended, such that the default CSV filename is localdata/gdrivelist-username@gmail.com.csv.

To download all of the files listed in the CSV file, use the `-csv` option.

`python3 kumodd.py -csv localdata/gdrivelist-username@gmail.com.csv`

To relay kumodd access though an HTTP proxy, use the -proxy option, or specify the proxy in config/config.cfg:
```
[proxy]
host = proxy.host.com
port = 8888
user = username (optional)
pass = password (optional)
```

The default config file is config/config.dat.  To select an alternate config file, use the -c option:

`python3 kumodd.py -c config/alternate.dat`

## Meta-data

Default meta-data include:

Name	| Description 
------:	| :-----------
createdDate             |  Last Modified time (UTC)
modifiedDate            |  Created time (UTC)
id                      |  [File ID](https://developers.google.com/drive/api/v3/about-files), an opaque, random string which is constant for the life of a file, even if the file name changes.
path                    |  Google Drive File Path
revisions               |  Number of revisions
lastModifyingUserName   |  Last Modified by (user name)
ownerNames              |  Owner (user name)
md5Checksum             |  MD5 digest.  File types that are native to Google Docs do not include an MD5 digest, where as non-native types such as MS Office do, as shown below.
modifiedByMeDate        |  Last Modified by Account Holder Date (UTC)
lastViewedByMeDate      |  Last Viewed by Account Holder Date (UTC)
shared                  |  shared (true/false)

One can change which meta-data are included, or their order, by specifyinig a comma
delimited list in the configuration file.

``` shell
[gdrive]
metadata = createdDate,modifiedDate,id,path,revisions,lastModifyingUserName,ownerNames,md5Checksum,modifiedByMeDate,lastViewedByMeDate,shared
```

A more complete list of names of the meta-data are described in the [Google Drive API Documentation](https://developers.google.com/drive/api/v3/reference/files).
A few of the available metadata item names are shown in the following sample of available metadata associated with a Google Doc.

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
 'exportLinks': {'application/epub+zip': 'https://docs.google.com/feeds/download/documents/export/Export?id=1B0IK0SYcsZePmbdZG99BqBtgXVW5py3JJY31W-l9do8&exportFormat=epub',
                 'application/pdf': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=pdf',
                 'application/rtf': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=rtf',
                 'application/vnd.oasis.opendocument.text': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=odt',
                 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=docx',
                 'application/zip': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=zip',
                 'text/html': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=html',
                 'text/plain': 'https://docs.google.com/feeds/download/documents/export/Export?id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&exportFormat=txt'},
 'iconLink': 'https://drive-thirdparty.googleusercontent.com/16/type/application/vnd.google-apps.document',
 'id': '1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8',
 'kind': 'drive#file',
 'labels': {'hidden': False,
            'restricted': False,
            'starred': False,
            'trashed': False,
            'viewed': True},
 'lastModifyingUser': {'displayName': 'John Doe',
                       'emailAddress': 'john.doe@gmail.com',
                       'isAuthenticatedUser': True,
                       'kind': 'drive#user',
                       'permissionId': '14466611316174614251',
                       'picture': {'url': 'https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}},
 'lastModifyingUserName': 'John Doe',
 'lastViewedByMeDate': '2019-06-24T05:41:17.095Z',
 'markedViewedByMeDate': '1970-01-01T00:00:00.000Z',
 'mimeType': 'application/vnd.google-apps.document',
 'modifiedByMeDate': '2019-06-24T05:41:17.095Z',
 'modifiedDate': '2019-06-24T05:41:17.095Z',
 'ownerNames': ['John Doe'],
 'owners': [{'displayName': 'John Doe',
             'emailAddress': 'john.doe@gmail.com',
             'isAuthenticatedUser': True,
             'kind': 'drive#user',
             'permissionId': '14466611316174614251',
             'picture': {'url': 'https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}}],
 'parents': [{'id': '0AIpnT_44h5smUk9PVA',
              'isRoot': True,
              'kind': 'drive#parentReference',
              'parentLink': 'https://www.googleapis.com/drive/v2/files/0AIpnT_44h5smUk9PVA',
              'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/parents/0AIpnT_44h5smUk9PVA'}],
 'quotaBytesUsed': '0',
 'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8',
 'shared': False,
 'spaces': ['drive'],
 'thumbnailLink': 'https://docs.google.com/a/feeds/vt?gd=true&id=1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8&v=5&s=AMedNnoAAAAAXRxA8DRkzkTPYWsf3mzIcWQlHVAxFmMB&sz=s220',
 'title': 'Untitled document',
 'userPermission': {'etag': '"_sqIxUq0fTLFIA17mBQDotbHWsg/zxcSjdx1q8ilez4u1L71gst1zd0"',
                    'id': 'me',
                    'kind': 'drive#permission',
                    'role': 'owner',
                    'selfLink': 'https://www.googleapis.com/drive/v2/files/1Bbouiss7ioabPembZdG9B9bsabaiudfjqBgtXV5-9ldo8/permissions/me',
                    'type': 'user'},
 'version': '12',
 'writersCanShare': True}
```

## Notes

To use kumod on windows, add python and git to the PATH environment variable, and then
do the rest of the setup.
``` shell
SET "PATH=%PATH%;C:\Python37"
SET "PATH=%PATH%;C:\ProgramFile\Git\bin"
git clone https://github.com/rich-murphey/kumodd.git
cd kumodd
python -m pip install --user -r requirements.txt
.\kumodd.py -l doc
```

Using an HTTP proxy on Windows does not work due to unresolved issues with httplib2.

Note that [Google rate limits API calls](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas).
At the time of writing, the default rate limits are:

- 1,000,000,000 queries per day
- 1,000 queries per 100 seconds per user
- 10,000 queries per 100 seconds

kumodd uses the [Google API Python
Client](https://github.com/googleapis/google-api-python-client) which is officially
supported by Google, and is feature complete and stable.  However, it is not actively
developed.  It has has been replaced by the [Google Cloud client
libraries](https://github.com/googleapis/google-cloud-python) which are in development,
and recommended for new work.

[gdrive]
