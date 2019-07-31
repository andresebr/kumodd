# Log2Timeline Export

[log2timeline](https://www.forensicswiki.org/wiki/Log2timeline) is a framework for
artifact timeline creation and analysis. There are both commercial and open source
forensics tools that support generating and analyzing log2timeline data. Analysis tools
that can combine log2timeline data with other sources for correllation include FTK
(commercial) and [Plaso](https://plaso.readthedocs.io/en/latest) (open source).

Kumodd's '-l2t' option reads cached metadata and exports a CSV file in log2timeline
format.  The CSV output is saved as filelist-l2t.username.csv.  The [log2timeline CSV
record format](https://forensicswiki.org/wiki/L2T_CSV) consists of 17 columns. The
Google Drive metadata are mapped to log2timeline columns as shown below.

The CSV output contains one record for each timestamp in the metadata.  Each file has
one or more created, viewed and modified timestamps. A file may also have multiple
revisions, and each revision has a modifiedDate timestamp.

These Google Drive metadata are mapped regardless of the kind of timestamp.

Google Drive Metadata | l2t column
:---------------- | :---
source	 | Google Drive
sourcetype | file
filename | fullpath 
inode	 | Google Drive file ID


For each different kind of Google Drive Timestamp, log2timeline columns are mapped as follows.

Google Drive Timestamp	| l2t MACB | l2t type	| l2t description	| l2t user			| l2t extra
:----------------	| :--- | :-------	| :--------		| :--------			| :--------
createdDate		| B    | Created	| Created		| First owner name			| 
lastViewedByMeDate	| A    | Last Accessed	| Last Viewed by Me	| Google Drive account name	| 
markedViewedByMeDate	| A    | Last Accessed	| Last Accessed 	| 
modifiedByMeDate	| M    | Last Modified	| Last Modified by Me	| Google Drive account name	| 
modifiedDate		| M    | Last Modified	| Last Modified		| 
revision modifiedDate	| M    | Last Modified	| Last Modified		| revision lastModifyingUser	| revision ID
