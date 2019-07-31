Kumodd will download malware or other abusive files if present. Kumodd does this by
setting acknowledgeAbuse=true when downloading files from Google Drive.

Using an HTTP proxy on Windows does not work due to unresolved issues with python 3's
httplib2 on Windows.

There are unresolved issues setting the Created time of files using the Windows API.
Although the Created Time is set on Windows, the value may fail to be preserved.

The Google Drive photos space was sunset in January 2018. Previously, changes in Google
Photos would sometimes fail to update the md5Checksum key in Google Drive, resulting in
a invalid MD5.  After the January 2018 sunset, [any changes made in Drive will only
apply to Drive. Any changes made in Photos will only apply to
Photos.](https://support.google.com/drive/answer/6156103).

[Google rate limits API
calls](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas) to 1,000
queries per 100 seconds per user. Kumodd does not batch requests to the Google Drive
API.  It makes one API call for each folder, one for each file to request all revisions
of the file, and one for each download.  For each folder, Kumodd request metadata of all
files in a folder. For each file, Kumodd requests all of the revisions of the given
file.  Other than that, requests are not batched. Even so, Kumodd is unlikely to exceed
these limits when downloading, due to the latency of the API.

## Future Work

Conversion of native Google Apps Docs, Sheets and slides to PDF or LibreOffice makes
their download much slower.  Change detection for native files is limited to the
modifiedDate value because file size and MD5 are not available via the API.  For native
Google Apps files, if the metadata is present, Kumodd could use the previously saved
metadata to detect whether the file has changed, using for instance, the revision ID.

Kumodd uses V2 of the [Google API Python
Client](https://github.com/googleapis/google-api-python-client) which is officially
supported by Google, and is feature complete and stable.  However, it is not actively
developed.  It has has been replaced by the [Google Cloud client
libraries](https://googleapis.github.io/google-cloud-python) which are in development,
and recommended for new work. It removes support for Python 2 in 2020.
