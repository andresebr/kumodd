# How to Search for Files

Use search query to limit results by the file's metadata.

## Examples

Download all files names that match \*2014\*:

	./kumodd -download all -q "title contains '2014'"

Download all files except files names that match \*hello\*:

	./kumodd -download all -q "not name contains 'hello'"

Download all files that contain the word 'thorax'. This is a full text search of file contents.

	./kumodd -download all -q "fullText contains 'thorax'"

Download all files edited by a given user:

	./kumodd -download all -q "'john.doe@gmail.com' in writers"

Download all files modified on or after 1/1/2012 00:00:00 UTC:

	./kumodd -download all -q "modifiedTime > '2012-01-01T00:00:00'"

List all PDFs viewed by the account holder on or after 1/1/2012 00:00:00 UTC:

	./kumodd -download pdf -q "viewedByMeTime > '2012-01-01T00:00:00'"

Dates are in RFC3339 format, and the default timezone is UTC.

For more details on the query syntax, see the [Google Drive API Referencce](https://developers.google.com/drive/api/v3/search-shareddrives).

Results include files in the trash. Files from the trash have the metadata attribute,
labels.trashed == true.

Results will include malware or other abusive files if present. Kumodd does this by
setting acknowledgeAbuse=true when downloading such files from Google Drive.

Results will include files in Team drives and Shared drives.

Results will not include Google Photos or application data.  To obtain them, see scope
and spaces below.

## Equivalent Filters

Filters are short names for file classifications, such as doc or image.  [How to Use
Kumodd](https://github.com/rich-murphey/kumodd/wiki/How-to-Use-Kumodd) shows examples of
using filiters. 

Each filter has an equivalent query, as follows.

Filter | Equivalent Query
:----- | :-----
-download doc | -download all -q "mimeType = 'application/msword'<br/>or  mimeType = 'application/vnd.openxmlformats-officedocument.wordprocessingml'<br/>or mimeType = 'application/vnd.ms-word'<br/>or mimeType = 'application/vnd.google-apps.document'"
-download  xls | -download all -q "mimeType = 'application/vnd.ms-excel'<br/>or mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml'<br/>or mimeType = 'application/vnd.google-apps.spreadsheet'"
-download ppt | -download all -q "mimeType = 'application/vnd.ms-powerpoint'<br/>or mimeType = 'application/vnd.openxmlformats-officedocument.presentationml'<br/>or mimeType = 'application/vnd.google-apps.presentation'"
-download pdf |  -download all -q "mimeType = 'application/pdf'"
-download text | -download all -q "mimeType contains 'text/'"
-download image | -download all -q "mimeType contains 'image/'"
-download audio | -download all -q "mimeType contains 'audio/'"
-download video | -download all -q "mimeType contains 'video/'"

Google Apps can open mimeTypes listed here: (https://developers.google.com/drive/api/v3/mime-types).

An extensive list of mimeTypes is listed in [MimeType.cs](https://github.com/google/google-drive-proxy/blob/master/DriveProxy/API/MimeType.cs).

 
