# How to Verify Data

There are two ways Kumodd can verify data:

* __-list__: List metadata in google drive, and use it to verify local files if present
* __-verify__: use local cached metadata to verify local files

When listing (__-list__ option), Kumodd
downloads metadata from Google Drive and verifies whether local data are consistent with Google Drive.  

When verifying (__-verify__ option), Kumodd uses the previously saved YAML metadata on
disk to verify whether files and metadata on disk are correct. If there are multiple
revisions, Kumodd verifies all downloaded revisions.  Because it uses cached metadata,
it does not connect to Google Drive, and does not require any network access or
credentials.

Either way (__-list__ or __-verify__ options), Kumodd confirms whether each file's MD5,
file size, and Last Modified and Last Accessed are correct.  In addition, it confirms
whether the MD5 of the metadata on disk matches the MD5 of the metadata originally read
from Google Drive.

### Download Google Drive Metadata to Verify Local Data

To retrieve metadata from Google Drive and review accuracy of the data and metadata on
disk, use the __-list__ option. 
``` shell
kumodd -list pdf -col verify
Status File MD5  Size      Mod Time  Acc Time  Metadata  fullpath
valid  match     match     match     match     match     ./My Drive/report_1424.pdf
```

### Verify Local Data Without Accessing Google Drive

To review accuracy of the data and metadata using previously downloaded metadata, use
the __-verify__ option. This does not read data from Google Drive, but rather
re-reads the previously saved YAML metadata on disk, and confirms whether the files'
MD5, size, Last Modified, and Last Accessed time are correct.  This also confirms
whether the MD5 of the metadata match the previously recorded MD5.

``` shell
kumodd -verify -col verify
Status File MD5  Size      Mod Time  Acc Time  Metadata  fullpath
valid  match     match     match     match     match     ./My Drive/report_1424.pdf
```
To show different columns, use the __-col__ option. To see the MD5s, use __ -col
md5s__. See [How to Configure](../How-to-Configure) for furhter usage of the __-col__ option.
``` shell
kumodd -verify -col md5s
Status File MD5  Size      Mod Time  Acc Time  Metadata  MD5 of File                      MD5 of Metadata                  fullpath
valid  match     match     match     match     match     5d5550259da199ca9d426ad90f87e60e 216843a1258df13bdfe817e2e52d0c70 ./My Drive/report_1424.pdf
```
To verify only the most recent version and ignore previous revisions, use __-norevisions__.
This can be significantly faster because with revisions there is one API call per file,
whereas with __-norevisions__ there is one API call per folder.

## Verify Data Using Other Tools 

The MD5 of the file contents is recorded in the metadata. 
``` shell
grep md5Checksum 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Checksum: 5d5550259da199ca9d426ad90f87e60e
```
When Kumodd saves a file, it rereads the file, and computes the MD5 digest of the
contents.  It compares the values and reports either __ matched__  or __ MISMATCHED__  in the
md5Match property.
``` shell
grep md5Match 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
md5Match: match
```
Other tools can be used to cross-check MD5 verification of file contents:
``` shell
md5sum 'download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml'
5d5550259da199ca9d426ad90f87e60e  download/john.doe@gmail.com/My Drive/My Drive/report_1424.yml
```

The MD5 of the redacted metadata is saved as yamlMetadataMD5:
``` shell
grep yamlMetadataMD5 'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'
yamlMetadataMD5: 216843a1258df13bdfe817e2e52d0c70
```

To verify the MD5 of the metadata, dynamic values are removed first (*see* [Data
Verification Methods](https://github.com/rich-murphey/kumodd/wiki/Methods)).  To filter and digest, [yq, a command line YAML
query tool](https://yq.readthedocs.io/), and md5sum may be used.

``` shell
yq -y '.|with_entries(select(.key|test("(Link|Match|status|Url|yaml|converted)")|not))' <'download/metadata/john.doe@gmail.com/My Drive/report_1424.pdf.yml'|md5sum
216843a1258df13bdfe817e2e52d0c70  -
```

During listing, if there are changes in the metadata, Kumodd will output diffs that
identify the values that changed between previously saved and Google Drive metadata.

## Reporting Differences in Metadata

When differences in metadata are detected, between on disk and in Google Drive, kumodd
show a diff on standard output that highlights the rows and columns of metadata
that changed.  To disable reporting of differences, use __-nodiffs__.

``` shell
kumodd -col short -list pdf
Status  Version Full Path
valid   4       ./My Drive/docs/paper.pdf
valid   3       ./My Drive/docs/article.pdf
INVALID 3       ./My Drive/docs/report(3).pdf
______________________ ./download/metadata/john.doe@gmail.com/./My Drive/docs/report(3).pdf
  capabilities:
    canAddChildren: false
    canChangeCopyRequiresWriterPermission: true
    canChangeViewersCanCopyContent: true
    canComment: true
    canCopy: true
    canDelete: true
    canDownload: true
    canEdit: true
    canListChildren: false
    canMoveItemIntoTeamDrive: true
    canMoveItemOutOfDrive: true
    canReadRevisions: true
    canRemoveChildren: false
    canRename: true
    canShare: true
    canTrash: true
    canUntrash: true
  category: pdf
  copyRequiresWriterPermission: false
- createdTime: '2018-08-04T12:55:13.682Z'
?                     ^  ------   ^  ^^
+ createdTime: '2018-07-27T05:24:14.659Z'
?                     ^ +++   +++ ^  ^^
  explicitlyTrashed: false
  fileExtension: pdf
  fullFileExtension: pdf
  fullpath: ./My Drive/docs/report(3).pdf
  hasThumbnail: true
- headRevisionId: 0B4pnT_44hsmZX0c0x22o5ZdaSzyanpUENCVFMWnVvPQ
- id: 1EEPPXweZb9p5_YsAkT-g8gpkwWhrv86X
+ headRevisionId: 0B4pnT_44h5mT0wZVEdVN63g4ZB4M1ncDNrQmZaU9NPQ
+ id: 1QHwKAAQz08iIjRydOXNPFb182D6wbtvD
  isAppAuthorized: false
  kind: drive#file
  lastModifyingUser:
    displayName: John Doe
    emailAddress: john.doe@gmail.com
    kind: drive#user
    me: true
    permissionId: '1466113117414251'
    photoLink: https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NR8xp9YvB2y/s64/photo.jpg
  md5Checksum: 30428a1e95780c79e738d7d9ba2
  mimeType: application/pdf
  modifiedByMe: true
- modifiedByMeTime: '2018-08-04T12:55:13.682Z'
?                          ^  ------   ^  ^^
+ modifiedByMeTime: '2018-07-27T05:24:14.659Z'
?                          ^ +++   +++ ^  ^^
- modifiedTime: '2018-08-04T12:55:13.682Z'
?                      ^  ------   ^  ^^
+ modifiedTime: '2018-07-27T05:24:14.659Z'
?                      ^ +++   +++ ^  ^^
  name: report.pdf
  originalFilename: report.pdf
  ownedByMe: true
  owners:
  - displayName: John Doe
    emailAddress: john.doe@gmail.com
    kind: drive#user
    me: true
    permissionId: '14466111617614251'
    photoLink: https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NR8xp9YvB2y/s64/photo.jpg
  parents:
- - 1_DnZ8H9h29V_zZVeaFGfdqX6N
+ - 1nVbNFRPHlA-_L2RW0RnjbIFss
  path: ./My Drive/0read
  permissionIds:
  - '1466613167464251'
  permissions:
  - deleted: false
    displayName: John Doe
    emailAddress: john.doe@gmail.com
    id: '1446613167464251'
    kind: drive#permission
    photoLink: https://lh5.googleusercontent.com/-ptN2vmCNOi8/AAAAAAAAAAI/AAAAAAAAGkE/NR8xp9YvB2y/s64/photo.jpg
    role: owner
    type: user
  quotaBytesUsed: '25417608'
  revisions: null
  shared: false
  size: '25417608'
  spaces:
  - drive
  starred: false
  thumbnailVersion: '1'
  trashed: false
  version: '3'
  viewedByMe: true
- viewedByMeTime: '2018-08-04T12:55:13.682Z'
?                        ^  ------   ^  ^^
+ viewedByMeTime: '2018-07-27T05:24:14.659Z'
?                        ^ +++   +++ ^  ^^
  viewersCanCopyContent: true
  writersCanShare: true
_______________________________________________________________________________

```
