# Kumo (Cloud) Data Dumper

Kumodd is a command line utility for forensic preservation of Google Drive cloud
storage.  It downloads files and metadata from a specified account in a verifiable
forensically sound manner. It requres authorized read-only access and uses public APIs. It
verifies the MD5 of each file and it's metadata. It integrates with timeline analysis
tools.

``` shell
kumodd --download doc
Created (UTC)            Last Modified (UTC)      Remote Path                   Revision   Modified by      Owner            MD5                       
2019-06-24T05:04:47.055Z 2019-06-24T05:41:17.095Z My Drive/Untitled document    3          Johe Doe         Johe Doe         -
2019-05-18T06:16:19.084Z 2019-05-18T06:52:49.972Z My Drive/notes.docx           1          Johe Doe         Johe Doe         1376e9bf5fb781c3e428356b4b9aa21c
2019-05-16T23:34:42.665Z 2019-05-17T22:18:07.705Z My Drive/Letter to John.docx  1          Johe Doe         Johe Doe         4cb0b987cb879d48f56e4fd2cfd57d83
2019-04-12T16:21:48.867Z 2019-04-12T16:21:55.245Z My Drive/Todo List            27         Johe Doe         Johe Doe         -                   
```
## Features
- [Limit results by full text search terms or metadata](guide/Search-Query)
- [Preserve extensive metadata of each file](guide/Example-Metadata).
- [Verify preservation of file contents and metadata](guide/Methods).
- [Export Google Docs, Sheets, Slides as PDF or LibreOffice.](guide/Command-line-options)
- [Export CSV file list with configurable columns](guide/How-to-Configure).
- [Export Log2Timeline for Analysis](guide/Log2Timeline-Export).

## User Guide
* [Usage Examples](guide/How-to-Use-Kumodd)
* [How to Install](guide/How-to-Install)  
* [How to Configure](guide/How-to-Configure)  
* [Default Configuration](guide/Default-configuration)  
* [Google Drive Metadata](guide/Metadata)  
* [How to Search for Files](guide/Search-Query)  
* [Data Verification Methods](guide/Methods)  
* [How to Verify Files](guide/How-to-Verify-Data)  
* [Log2Timeline Export](guide/Log2Timeline-Export)
* [Command Line Options](guide/Command-line-options)  
* [How to Test Kumodd](guide/How-to-Test-Kumodd)  
* [Example Metadata](guide/Example-Metadata)  
* [References](guide/References)  
* [How to Build](devel/How-to-Build)  
* [Limitations](devel/Limitations)  
