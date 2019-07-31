# Data Verification Methods

Kumodd verifies both data and metadata. Files are verified by comparing the MD5, size,
and Last Modified time.  Kumodd can report whether each matches the metadata, as shown
in [How to Verify Data](https://github.com/rich-murphey/kumodd/wiki/How-to-Verify-Data).

Metadata		| Description
:----			| :----
md5Checksum		| MD5 of the data.
md5Match		| match if MD5 on disk = from Google Drive.
fileSize		| Size (bytes) of the data from Google Drive.
sizeMatch		| match if local size = size in google drive, else MISMATCH.
modifiedDate		| Last Modified time (UTC) of the data in Google Drive.
modTimeMatch		| match if Last Modified time on disk = in Google Drive.
lastViewedByMeDate	| Last Viewed By Account User (UTC) on disk = in Google Drive.
accTimeMatch		| match if lastViewedByMeDate and FS Last Access Time are equal.
yamlMetadataMD5		| MD5 of the redacted metadata.
yamlMD5Match		| match if metadata MD5 on disk = data from Google Drive.

Google Drive has several native file formats, including Docs, Sheets, Slides, Forms, and
Drawings. These native formats are always converted by Google Drive during upload or
download, and their available API metadata excludes the size and MD5.  For these native
files, Kumodd computes the size and MD5 in memory during download, prior to writing the
file to disk, and Kumodd adds the missing MD5 and size to the metadata.  As a result,
all files have a size and MD5 computed prior to writing to disk.

To verify files, data is always re-read from disk in order to compare the MD5 of the
data on disk to the MD5 reported by googel drive or computed in memory upon download.
This is true for for all modes of operation: downloading files (-download), downloading
metadata (-list), downloading a file list (-csv) or verifying files using locally cached
metadata (-verify).  

When downloading, if a file exists, but any of the MD5, size or Last Modified time
differ between Google Drive's reported values and the values on disk, then kumodd will
re-download the file and save the updated YAML metadata.  Next, Kumodd will re-read the
saved file and metadata to ensure the MD5, size and time stamp on disk are valid.

Change detection differs for native Google Apps files because the API does not provide a
size or MD5 for them.  Changes in Google Apps files are detected by the Last Modified
time alone.

Kumodd also verifies bulk metadata, saved on disk in YAML format. However, certain
metadata are dynamic while others are static.  Dynamicly generated items are valid for a
limited time after they are downloaded, after which a subsequent download of metadata
retrieves differing values. For example, the value of 'thumbnailLink' changes every time
the metadata is retrieved from Google Drive.  Other 'Link' and URL values change after a
few weeks. For Google Apps files, dynamicly generated metadata includes the computed MD5
and size of the converted file. Before computing the MD5 of the YAML metadata, Kumodd
removes all dynamic metadata. Dynamic metadata are those having keys names containing
the words: Link, Match, status, Url or yaml.  When these keys are removed, the metadata
is reproducible (identical each time retrieved from Google Drive, and unique on disk) if
the file has not changed.
