# Google Drive Metadata

Metadata of each file is preserved in YAML format (*see* [Example raw
metadata](https://github.com/rich-murphey/kumodd/wiki/Example-Metadata)).  By default, files are stored in a path in
./download, and their metadata in ./download/metadata.  For foo.doc, the file and its
metadata paths would be:
- ./download/john.doe@gmail.com/My Drive/foo.doc
- ./download/metadata/john.doe@gmail.com/My Drive/foo.doc.yml

## Time Stamps

Google Drive time stamps have millisecond resolution. Typical Windows and Unix
file systems have greater resolution. In practice this allows Kumodd to set file system
time stamps to match exactly the time stamps in Google Drive.

Kumodd maps Google Drive time stamps to file system time stamps as follows:

Google Drive Time Stamp	| File System Time Stamp
:----------------	| :----------------
modifiedDate		| Last Modified time
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

If file system time stamps are to be used in analysis, the -verify option can be used to
verify they are consistent with the metadata.  External tools can be used as well for
verification of accuracy.  Given a downloaded file set, kumodd -verify will verify the
file system time stamps are equal to the time stamps that were retrieved from the Google
Drive API.

## Duplicate File Names

Google Drive folders can hold duplicate file names that are differentiated by their
version number. Unix and Windows file systems require filenames within a folder are
unique.  So, for version number except 1, kumodd appends '_(v<version>)' before the file
extension.  For example: ./My Drive/Untitled document_(v12).pdf

