If config/config.yml does not exist, kumodd will create it, as shown below. The default
column set is 'normal'.

``` yaml
gdrive:
  gdrive_auth: config/gdrive_config.json
  oauth_id: config/gdrive.dat
  csv_prefix: ./filelist-
  csv_columns:
    short:
    - [status, 7]
    - [version, 7]
    - [fullpath, 66]
    verify:
    - [status, 7]
    - [md5Match, 7]
    - [sizeMatch, 7]
    - [modTimeMatch, 7]
    - [accTimeMatch, 7]
    - [yamlMD5Match, 7]
    - [fullpath, 60]
    md5s:
    - [status, 7]
    - [md5Match, 7]
    - [sizeMatch, 7]
    - [modTimeMatch, 7]
    - [accTimeMatch, 7]
    - [yamlMD5Match, 7]
    - [md5Checksum, 32]
    - [yamlMetadataMD5, 32]
    - [fullpath, 60]
    owners:
    - [status, 7]
    - ['owners[*].emailAddress', 20]
    - [fullpath, 50]
    normal:
    - [name, 20]
    - [category, 4]
    - [status, 7]
    - [md5Match, 7]
    - [sizeMatch, 7]
    - [modTimeMatch, 7]
    - [accTimeMatch, 7]
    - [yamlMD5Match, 7]
    - [fullpath, 60]
    - [version, 6]
    - [revision, 8]
    - [ownerNames, 20]
    - [size, 9]
    - [modifiedTime, 24]
    - [createdTime, 24
    - [mimeType, 22]
    - [id, 44]
    - [lastModifyingUserName, 22]
    - [md5Checksum, 32]
    - [modifiedByMeTime, 24
    - [lastViewedByMeTime, 24]
    - [shared, 6]
    test:
    - [md5Checksum, 32]
    - [status, 7]
    - [name, 60]

csv_title:
  accTimeMatch: AccTimeOK
  app: Application
  appDataContents: App Data
  capabilities: Capabilities
  category: Category
  copyRequiresWriterPermission: CopyRequiresWriterPermission
  copyable: Copyable
  createdTime: Created (UTC)
  downloadUrl: Download
  editable: Editable
  embedLink: Embed
  explicitlyTrashed: Was Trashed
  exportLinks: Export
  fileExtension: EXT
  fullpath: Full Path
  headRevisionId: HeadRevisionId
  iconLink: Icon Link
  id: File Id
  kind: Kind
  labels: Labels
  lastModifyingUserName: Last Mod By
  lastViewedByMeTime: My Last View
  'lastModifyingUser.emailAddress': Last Mod Email
  local_path: Local Path
  md5Checksum: MD5 of File
  md5Match: MD5OK
  mimeType: MIME Type
  modTimeMatch: ModTimeOK
  modifiedByMeTime: My Last Mod (UTC)
  modifiedTime: Last Modified (UTC)
  name: Name
  originalFilename: Original File Name
  ownerNames: Owner
  owners: Owners
  'owners[*].emailAddress':  Owners
  parents: Parents
  path: Path
  quotaBytesUsed: Quota Used
  revision: Revisions
  selfLink: Self Link
  shared: Shared
  size: Size(bytes)
  sizeMatch: SizeOK
  spaces: Spaces
  status: Status
  trashed: In Trash
  user: User
  userPermission: User Permission
  version: Version
  webContentLink: Web Link
  writersCanShare: CanShare
  yamlMetadataMD5: MD5 of Metadata
```
