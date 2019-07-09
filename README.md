# kumodd

Kumodd downloads files and their metadata from a specified Google
Drive account in a forensically sound manner.

- Files can be filtered by category, such as doc, image, or video.  
- Extensive Google Drive metadata of each file is preserved as a corresponding YAML file.  
- Metadata columns of exported CSV may be selected in the configuration file.  
- Last Modified time stamp is preserved and verified.  
- MD5 digest is preserved and verified.
- File size is preserved and verified.
- Metadata is preserved and verified.

## Usage examples

Both the list (-l) and download (-d) options create a CSV file and a text table on
standard output.

List (-l) all documents:
``` shell
kumodd.py -l doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```

Download (-d) all documents to ./download (the default location).

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

As a convenience, kumodd sets the time stamps of files that are exported.  However, due
to file system and kernel limitations, the only reliable file system timestamp is the
Last Written time of exported files.  Other file system time stamps on exported files
are unreliable. For any analysis, time stamps should instead be taken directly from the
preserved metadata (e.g. foo.doc.yml metadata for a given foo.doc).

Time stamps available in Google Drive generally includes the following:
- createdDate
- markedViewedByMeDate
- modifiedByMeDate
- modifiedDate

To set the timestamps in exported files, Kumod maps these values as follows:
- Last Modified time = modifiedDate
- Last Accessed time = markedViewedByMeDate
- Created time = createdDate

Windows has all three; however, setting the Created time in python via the win32 API has
proven unreliable.  Certain more recent Unix file systems have a created time stamp,
including Ext4, UFS2, Hammer, LFS, and ZFS (*see* [Wikipedia Comparison of File
Systems](https://en.wikipedia.org/wiki/Comparison_of_file_systems)).  However, the Linux
kernel provides no method (e.g. system call or library) to read or write the Created
time, so Created time is not available to kumodd on Linux.  markedViewedByMeDate is
not always available in Google Drive.  The Last Accessed time stamps may be overwritten
by subsequent reading of exported files.

In conclusion, file system time stamps on exported files should not be relied on for any
analysis.  Instead of file system time stamps, analysis should use the time stamps taken
directly from the preserved metadata.

## Metadata

Google Drive API Metadata of each file is preserved in YAML format (*see* [Example raw
metadata](#example-raw-metadata)).  Files are stored in ./download and their
corresponding metadata are saved in ./download/metadata.  For foo.doc, the file and its
metadata paths would be:
- ./download/john.doe@gmail.com/My Drive/foo.doc
- ./download/metadata/john.doe@gmail.com/My Drive/foo.doc.yml

## File Validation

When Kumodd saves a file, it also computes the MD5 digest of the contents.  
Kumodd saves it as 'md5Local' in the metadata.
``` shell
grep md5Local 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Local: 5d5550259da199ca9d426ad90f87e60e
```
For certain file types (exclding Google Apps files), Google Drive provides an MD5 of the
data.
``` shell
grep md5Checksum 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Local: 5d5550259da199ca9d426ad90f87e60e
```
When this is present, kumodd verifies Google Drive's MD5 (md5Checksum) is identical to
the file's MD5 (md5Local). This ensures that the file on disk is identical to the file in Google Drive.
Kumodd also records whether they match in the metadata 'md5Match':
``` shell
grep md5Match 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Match: match
```
The MD5 of the file can be verified using other tools:
``` shell
md5sum 'download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml'
5d5550259da199ca9d426ad90f87e60e  download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml
```

In summary, Kumodd saves metadata for the file's MD5 in the following:
Content MD5 Metadata	| Value
----:			| :----
md5Checksum		| MD5 of the data in Google Drive. Not preset for Google Apps files.
md5Local		| MD5 of the file's contents on disk.
md5Match		| match if md5Local == md5Checksum. n/a if there is no md5Checksum. Else MISMATCH.


Similaryly, Kmodd compares the file size to that in Google Drive:
File Size Metadata	| Value
----:			| :----
fileSize		| Size (bytes) of the data in Google Drive.
localSize		| Size (bytes) file on disk.
md5Match		| match if localSize == fileSize, else MISMATCH.

Similaryly, Kmodd compares the file system Last Modified time to Google Drive's modifiedDate:
Last Mod Metadata	| Value
----:			| :----
modifiedDate		| Last Modified time (UTC) of the data in Google Drive.
md5Match		| match if Last Modified time in Google Drive and on disk are equal.

Validation is performed when listing or downloading files. Validation limited to
available data. Native Google Apps and certain PDF files do not provide a MD5
digest. Last Modify time is the only reliable file system time stamp.  To detect
changes, kumod compares the MD5, file size and Last Modify time.

When downloading, if any of MD5, file size or Last Modify time differ from Google
Drive's metadata, kumodd will download and update the file and YAML metadata. Next, it
will re-read the file to recompute the md5Match, sizeMatch and modTimeMatch, to ensure
the reported values reflect what is on disk.

In Kumodd output, md5Match, sizeMatch and modTimeMatch report the comparison between the
file on disk and the metadata in Google Drive at the time kumodd was run.

## Metadata Verification

Kumodd also verifies metadata. However, some of the values must be excluded because they
are inconsistent. For example, the value of 'thumbnailLink' changes every time the
metadata is retrieved from Google Drive.  Other 'Link' values may change after a few weeks.

Kumod saves the complete metadata in a YAML file.  Before computing the MD5, Kumod
redacts all metadata names containing the words: Link, Match, status, Url and yaml.
When these names are redacted, the metadata is reproducible (identical each time
retrieved from Google Drive, and unique on disk) if the file has not changed.

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
The validations can be reviewed by selecting the 'match' metadata items:
``` yaml
  csv_columns: status,md5Match,sizeMatch,modTimeMatch,yamlMD5Match,yamlMetadataMD5,fullpath
```
In which case Kumodd output looks like this:
``` shell
Status Drive MD5 sizeMatch Mod Time  YAML MD5  fullpath
verify match     match     match     match     ./My Drive/report_1424.pdf
```

## Metadata Output

One can configure which columns are written to stdout and CSV files.  They are specified
by the tag 'csv_columns' in config/config.yml (*see* [Configuration](#configuration)).
The default CSV columns are:

CSV Columns		| Description 
------:			| :-----------
title			| File name
category		| one of: doc, xls, ppt, text, pdf, image, audio, video or other
modifiedDate            | Last Modified Time (UTC)
modTimeMatch		| 'match' if local and remote Last Modification times match, else MISMATCH.
md5Checksum             | MD5 digest of remote file. None if file is a native Google Apps Document.
md5Local		| md5 of download if new or updated.  Otherwise None
md5Match		| 'match' if local and remote MD5s match, else time difference.
fileSize		| Number of bytes in file
sizeMatch		| 'match' if local and remote sizes match, else %local/remote.
revision                | Number of available revisions
ownerNames              | A list of owner user names
createdDate             | Created Time (UTC)
mimeType		| MIME file type
path                    | File path in Google Drive 
id                      | Unique [Google Drive File ID](https://developers.google.com/drive/api/v3/about-files)
lastModifyingUserName   | Last Modified by (user name)
modifiedByMeDate        | Time Last Modified by Account Holder (UTC)
lastViewedByMeDate      | Time Last Viewed by Account Holder (UTC)
shared                  | Is shared (true/false)

Note: The 'thumbnailLink' attribute is transient. Kumodd removes 'thumbnailLink' because
it changes each time the metadata is retrieved from Google Drive, even if the file and
other metadata have not changed.  When 'thumbnailLink' is excluded, the metadata is
reproducible (identical each time retrieved) if the file has not changed.  This also
improves time efficient review of changes in the YAML using 'diff'.

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
      -d,--get_items: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: Download files and create directories, optionally filtered by category
      -l,--list_items: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: List files and directories, optionally filtered by category
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
------:	| :-----------
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
  csv_columns: title,category,modTimeMatch,md5Match,revision,ownerNames,fileSize,modifiedDate,createdDate,mimeType,path,id,lastModifyingUserName,md5Checksum,md5Local,modifiedByMeDate,lastViewedByMeDate,shared

csv_title:
  app:			Application
  category:		Category
  createdDate:		Created (UTC)
  fileSize:		Bytes
  id:			File Id
  index:		Index
  lastModifyingUserName: Modified by
  lastViewedByMeDate:	My Last View
  local_path:		Local Path
  md5Checksum:		MD5
  md5Local:		Local MD5
  md5Match:		MD5s
  mimeType:		MIME Type
  modTimeMatch:		Mod Time
  modifiedByMeDate:	My Last Mod
  modifiedDate:		Last Modified (UTC)
  ownerNames:		Owner
  path:			Remote Path
  revision:		Revisions
  shared:		Shared
  status:		Status
  time:			Time (UTC)
  title:		Name
  user:			User
  version:		Version
```

Config item	| Description
-----:		| :-----
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
lastModifyingUserName: John Doe
local_path: ./download/john.doe@gmail.com/./My Drive/report.pdf
markedViewedByMeDate: '1970-01-01T00:00:00.000Z'
md5Checksum: 5d5550259da199ca9d426ad90f87e60e
md5Local: 5d5550259da199ca9d426ad90f87e60e
md5Match: match
mimeType: application/pdf
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
revision: '1'
selfLink: https://www.googleapis.com/drive/v2/files/0s9b2T_442nb0MHBxdmZo3pwnaGRiY01LbmVhcEZEa1FvTWtJ
shared: false
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
