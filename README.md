# kumodd

Kumodd downloads files and their metadata from a specified Google
Drive account in a forensically sound manner.

- Files can be filtered by category, such as doc, image, or video.  
- Extensive Google Drive metadata of each file is preserved as a corresponding YAML file.  
- Metadata columns of exported CSV may be selected in the configuration file.  
- Last Modified and Last Accessed times on disk are verified.  
- MD5 of file on disk is verified.
- File size on disk is verified.
- MD5 of bulk metadata on disk is verified.

## Usage examples

To list all documents (google doc, .doc, .docx, .odt etc), use:
``` shell
kumodd.py -l doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

Download (-d) all documents to ./download (the default location):

    kumodd.py -d doc

Download (-d) all PDF files to path (-p) /home/user/Desktop/:

    kumodd.py -d pdf -p /home/user/Desktop/

By default, native Google Apps files (docs, sheets and slides) are downloaded in PDF
format. To instead download them in LibreOffice format, use the '--nopdf' option.

By default, every available revision is downloaded unless --norevisions is specified, in
which case only the current file (latest revision) is downloaded.  Previous
revisions are saved as filename_(revision id_last modified date).

To download all of the files listed in a previously generated CSV file, use:

    kumodd.py -csv ./filelist-username.csv

## Duplicate File Names

Google Drive folders can hold duplicate file names that are differentiated by their
version number. Unix and Windows file systems require filenames within a folder are
unique.  So, in order to save various version of a given file, kumodd appends
'(version)' before the extension.  For example: ./My Drive/Untitled document(12).pdf

## Time Stamps

Google Drive time stamps have millisecond resolution. Typical Windows and Unix
file systems have greater resolution. In practice this allows Kumodd to set file system
time stamps to match exactly the time stamps in Google Drive.

Kumod maps Google Drive time stamps to file system time stamps as follows:

Google Drive Time Stamp	| File System Time Stamp
:----------------	| :----------------
modifiedByMeDate	| Last Modified time
lastViewedByMeDate	| Last Accessed time
createdDate		| Created time

Last Access times can be altered by subsequent access to downloaded files.  This can be
avoided on Linux using the noatime mount option.  It can be avoided on Windows using
fsutil behavior set disablelastaccess 1.

Created Time can be set on Windows NTFS; however, setting the Created time in python via
the win32 API has proven unreliable.  On Unix, certain more recent file systems have a
created time stamp, including Ext4, UFS2, Hammer, LFS, and ZFS (*see* [Wikipedia
Comparison of File Systems](https://en.wikipedia.org/wiki/Comparison_of_file_systems)).
However, the Linux kernel provides no method (e.g. system call or library) to read or
write the Created time, so Created time is not available to kumodd on Linux.
So, although the Created Time is set on Windows, it is often incorrect.

Caution is advised for any use of file system time stamps for analysis unless their
accuracy is verified by the analyst. Both Kumodd and external tools can be used for
verification of accuracy.  After downloading files using kumod -d, the timestamps can be
re-verified using kumodd -l.  For analysis, if file system time stamps are used, they
should be be verified by comparing them to the time stamps preserved in the YAML
metadata preserved exactly as retrieved from the Google Drive API.

## Metadata

Google Drive API Metadata of each file is preserved in YAML format (*see* [Example raw
metadata](#example-raw-metadata)).  Files are stored in ./download and their
corresponding metadata are saved in ./download/metadata.  For foo.doc, the file and its
metadata paths would be:
- ./download/john.doe@gmail.com/My Drive/foo.doc
- ./download/metadata/john.doe@gmail.com/My Drive/foo.doc.yml

## File Validation

Kumodd validates files by comparing their MD5, size, Last Modified, and Last Acceessed
time.  It reports whether they match in correspnding properties.  Kmodd stores these in
the YAML metadata file correesponding to each file.

Metadata		| Description
:----			| :----
md5Checksum		| MD5 of the data in Google Drive. Not preset for Google Apps files.
md5Match		| match if MD5 on disk = in Google Drive. n/a if there is no md5Checksum. Else MISMATCH.
fileSize		| Size (bytes) of the data in Google Drive.
sizeMatch		| match if local size = size in google drive, else MISMATCH.
modifiedByMeDate	| Last Modified time (UTC) of the data in Google Drive.
modTimeMatch		| match if Last Modified time in Google Drive and on disk are equal.
lastViewedByMeDate	| Last Viewed By Account User (UTC) of the data in Google Drive.
accTimeMatch		| match if lastViewedByMeDate and FS Last Access Time are equal.

For certain file types (excluding Google Apps files), Google Drive provides an MD5 of the
data. 
``` shell
grep md5Checksum 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Checksum: 5d5550259da199ca9d426ad90f87e60e
```
When Kumodd saves a file, it rereads the file, and computes the MD5 digest of the
contents.  It compares the values and reports either 'matched' or 'MISMATCHED' in the
md5Match property.
``` shell
grep md5Local 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Match: match
```
Other tools can be used to cross-check MD5 validation of file contents:
``` shell
md5sum 'download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml'
5d5550259da199ca9d426ad90f87e60e  download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml
```

Validation is performed when listing or downloading files.  Native Google Apps and
certain PDF files do not provide a MD5 digest. To detect changes, kumod compares the
file size and Last Modify time.

When downloading, if any of MD5 (if available), file size or Last Modify time differ
from Google Drive's metadata, kumodd will re-download the file and update tye YAML
metadata. Next, it will re-read the file to recompute the md5Match, sizeMatch and
modTimeMatch, to ensure that values on disk are valid.

## Metadata Verification

Kumodd also verifies bulk metadata. However, certain metadata values change
inconsistenly, and therefore must be excluded. For example, the value of 'thumbnailLink'
changes every time the metadata is retrieved from Google Drive.  Other 'Link' values may
change after a few weeks.  Still others are computed by Kmodd and are excluded because
they are a result of the comparison itself.

Kumod saves the complete, undredacted metadata in a YAML file.  Before computing the
bunk MD5 of the metadata, Kumod redacts all metadata names containing the words: Link,
Match, status, Url and yaml.  When these names are redacted, the metadata is
reproducible (identical each time retrieved from Google Drive, and unique on disk) if
the file has not changed.

The MD5 of the redacted metadata is saved as yamlMetadataMD5:
``` shell
grep yamlMetadataMD5 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
yamlMetadataMD5: 216843a1258df13bdfe817e2e52d0c70
```
The MD5 of the redacted metadata on disk can be verified independetly as follows:
``` shell
sudo -Hi python -m pip install yq
yq -y '.|with_entries(select(.key|test("(Link|Match|status|Url|yaml)")|not))' <'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'|md5sum
216843a1258df13bdfe817e2e52d0c70  -
```

## Verification Summary

Accuracy the data and metadata on disk can be verified using the following CSV columns:
``` yaml
  csv_columns: status,md5Match,sizeMatch,modTimeMatch,adccTimeMatch,yamlMD5Match,fullpath
```
After downloading, Kumodd rereads the data on disk, and reports whether downloaded files
succesfully validate.
``` shell
kumod.py --download pdf
Status File MD5  Size      Mod Time  Acc Time  Metadata  fullpath
valid  match     match     match     match     match     ./My Drive/report_1424.pdf
```

When listing files, Kumodd rereads the data on disk, reretrieves metadata from Google
Drive, and reports whether downloaded files succesfully verifies both file contents and
metadata vs that in Google Drive at the time kumod runs.
``` shell
kumod.py --list pdf
Status File MD5  Size      Mod Time  Acc Time  Metadata  fullpath
valid  match     match     match     match     match     ./My Drive/report_1424.pdf
```

## Metadata Output

One can configure which columns are written to stdout and CSV files.  They are specified
by the tag 'csv_columns' in config/config.yml (*see* [Configuration](#configuration)).
The default CSV columns are:

CSV Columns		| Description 
:------			| :-----------
title			| File name
category		| one of: doc, xls, ppt, text, pdf, image, audio, video or other
modifiedByMeDate	| Last Modified Time (UTC)
lastViewedByMeDate	| Time Last Viewed by Account Holder (UTC)
md5Checksum             | MD5 digest of remote file. None if file is a native Google Apps Document.
md5Match		| 'match' if local and remote MD5s match, else time difference.
fileSize		| Number of bytes in file
sizeMatch		| 'match' if local and remote sizes match, else %local/remote.
revision                | Number of available revisions
ownerNames              | A list of owner user names
createdDate             | Created Time (UTC)
mimeType		| MIME file type
path                    | File path in Google Drive 
id                      | Unique [Google Drive File ID](https://developers.google.com/drive/api/v3/about-files)
shared                  | Is shared in Google Drive to other users (true/false)

Metadata names are translated to CSV column titles using 'csv_title' in the
configuration file (*see* [Configuration](#configuration)).  If a title is not defined
there, the metadata name is used as the CSV column title.

## Setup

To setup kumodd, install python and git, then install kumodd and requirements, obtain an Oauth ID required for
Google API use, and finally, authorize access to the specified account.

1. Install python 3 and git. Then download kumodd and install the dependencies.

    On Debian or Ubuntu:

    ``` shell
    apt install python3 git
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python3 -m pip install --user -r requirements.txt
    ./kmodd.py --helpfull
    ```

    On Windows, one option is to use the [Chocolatey package
    manager](https://chocolatey.org/install).

    ``` shell
    cinst -y python git
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python -m pip install --user -r requirements.txt
    ./kmodd.py --helpfull
    ```

1. Obtain a Google Oauth client ID (required for Google Drive API):

    1. [Create a free google cloud account](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account).  
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
    
    If there is no local browser, or if --nobrowser is used, kumodd will
    instead print a URL of the login page.
    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  Next, it will request approval.
    1. Click "Approve". Next, the page will show an access token.
    1. Copy the token from the web page. Paste it into kumodd, and press enter. Next, kumodd saves the
    Oauth token in config/gdrive.dat.

    Once authorized, the login page will not be shown again unless the token
    expires or config/gdrive.dat is deleted.

## Usage

    ./kumodd.py [flags]

    flags:
      -p,--destination: Destination file path
        (default: './download')
      -d,--download: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: Download files and create directories, optionally filtered by category
      -l,--list: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: List files and directories, optionally filtered by category
      --log: <DEBUG|INFO|WARNING|ERROR|CRITICAL>: Set the level of logging detail.
        (default: 'ERROR')
      -m,--metadata_destination: Destination file path for metadata information
        (default: './download/metadata')
      -csv,--usecsv: Download files from the service using a previously generated CSV file
        (a comma separated list)
      --[no]browser: open a web browser to authorize access to the google drive account
        (default: 'true')
      -c,--config: config file
        (default: 'config/config.yml')
      --gdrive_auth: Google Drive account authorization file.  Configured in config/config.yml if not specified on command line.
      --[no]pdf: Convert all native Google Apps files to PDF.
        (default: 'false')
      --[no]revisions: Download every revision of each file.
        (default: 'true')
    
    Try --helpfull to get a list of all flags.
    
    
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

To relay kumodd access though an HTTP proxy, specify the proxy in config/config.yml:
``` yaml
proxy:
  host: proxy.host.com
  port: 8888 (optional)
  user: username (optional)
  pass: password (optional)
```

## Configuration

Command line arguments are used for configuration specific to a data set or case, while
a YAML file is used for configuration items not specific to a data set or case.  This is
intended to support reproducibility.  Multiple configuration files can be used to
generate multiple arrangements of CSV columns.

If config/config.yml does not exist, kumodd will create it using:
``` yaml
gdrive:
  gdrive_auth: config/gdrive_config.json
  oauth_id: config/gdrive.dat
  csv_prefix: ./filelist-
  csv_columns: title,category,modTimeMatch,md5Match,revision,ownerNames,fileSize,modifiedByMeDate,createdDate,mimeType,path,id,lastModifyingUserName,md5Checksum,md5Local,modifiedByMeDate,lastViewedByMeDate,shared

csv_title:
  accTimeMatch: Acc Time
  app: Application
  appDataContents: App Data
  capabilities: Capabilities
  category: Category
  copyRequiresWriterPermission: CopyRequiresWriterPermission
  copyable: Copyable
  createdDate: Created (UTC)
  downloadUrl: Download
  editable: Editable
  embedLink: Embed
  etag: Etags
  explicitlyTrashed: Trashed
  exportLinks: Export
  fileExtension: EXT
  fileSize: Size(bytes)
  fullpath: Full Path
  headRevisionId: HeadRevisionId
  iconLink: Icon Link
  id: File Id
  kind: Kind
  labels: Labels
  lastModifyingUserName: Last Mod By
  lastViewedByMeDate: My Last View
  local_path: Local Path
  md5Checksum: MD5
  md5Local: Local MD5
  md5Match: MD5s
  mimeType: MIME Type
  modTimeMatch: Mod Time
  modifiedByMeDate: My Last Mod (UTC)
  modifiedDate: Last Modified (UTC)
  originalFilename: Original File Name
  ownerNames: Owner
  owners: Owners
  parents: Parents
  path: Path
  quotaBytesUsed: Quota Used
  revision: Revisions
  selfLink: Self Link
  shared: Shared
  sizeMatch: Size
  spaces: Spaces
  status: Status
  thumbnailLink: Thumbnail
  time: Time (UTC)
  title: Name
  user: User
  userPermission: User Permission
  version: Version
  webContentLink: Web Link
  writersCanShare: CanShare
```

Name		| Description
:-----		| :-----
gdrive_auth	| filename of the google drive account authorization. Ignored if provided on command line.
oauth_id	| filename of the Oauth client ID credentials
csv_prefix	| the leading portion of the CSV file path.  Username and .csv are appended.
csv_title	| list of column titles for each metadata name


## Caveats

Downloading native Google Apps docs, sheets and slides is much slower than non-native
files, because format conversion to PDF of LibreOffice is required.

Using an HTTP proxy on Windows does not work due to unresolved issues with python 3's
httplib2.

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

## Developer Notes

To get debug logs to stdout, set 'log_to_stdout: True' in config.yml.

## Example raw metadata

Metadata provided by the Google Drive are described in the [Google Drive API
Documentation](https://developers.google.com/drive/api/v3/reference/files).  A few of
the available metadata are shown in the following YAML. This is the metadata of a PDF
file.

``` yaml
accTimeMatch: match
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
fullpath: ./download/john.doe@gmail.com/./My Drive/report.pdf
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
lastModifyingUserName: John Doe
lastViewedByMeDate: '1970-01-01T00:00:00.000Z'
markedViewedByMeDate: '1970-01-01T00:00:00.000Z'
md5Checksum: 5d5550259da199ca9d426ad90f87e60e
md5Match: match
mimeType: application/pdf
modTimeMatch: match
modifiedByMeDate: '2017-09-28T20:09:49.062Z'
modifiedDate: '2017-09-28T20:09:49.062Z'
originalFilename: report.pdf
ownerNames: [John Doe]
owners:
- displayName: John Doe
  emailAddress: john.doe@gmail.com
  isAuthenticatedUser: true
  kind: drive#user
  permissionId: '14466611316174614251'
  picture: {url: 'https://lh5.googleusercontent.com/-ptNwlcuNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NRxpYvByBx0/s64/photo.jpg'}
parents:
- {id: 0AIpnT_44h5smUk9PVA, isRoot: true, kind: drive#parentReference, parentLink: 'https://www.googleapis.com/drive/v2/files/0AIpnT_44h5smUk9PVA',
  selfLink: 'https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/parents/0AIpnT_44h5smUk9PVA'}
path: ./My Drive/report.pdf
quotaBytesUsed: '2843534'
revisions: null
selfLink: https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ
shared: false
sizeMatch: match
spaces: [drive]
status: update
title: report.pdf
userPermission: {etag: '"_sblwcq0fTsl4917mBslb2bHWsg/TpnHf_kgQXZabQ7VDW-96dK3owM"',
  id: me, kind: drive#permission, role: owner, selfLink: 'https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ/permissions/me',
  type: user}
version: '5'
webContentLink: https://drive.google.com/a/murphey.org/uc?id=0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ&export=download
writersCanShare: true
```
