# Kumo (Cloud) Data Dumper

Kumodd is a command line utility for forensic preservation of Google Drive cloud
storage.  It downloads files and metadata from a specified account in a verifiable
forensically sound manner. It requres authorized access and uses public APIs.  It
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
- [Limit results by full text or metadata search terms](https://github.com/rich-murphey/kumodd/wiki/Search-Query)
- [Preserve extensive metadata of each file](https://github.com/rich-murphey/kumodd/wiki/Example-Metadata).
- [Verify preservation of file contents and metadata](https://github.com/rich-murphey/kumodd/wiki/Methods).
- [Export Google Docs, Sheets, Slides as PDF or LibreOffice.](https://github.com/rich-murphey/kumodd/wiki/Command-line-options)
- [Export CSV file list with configurable columns](https://github.com/rich-murphey/kumodd/wiki/How-to-Configure).
- [Export Log2Timeline for Analysis](https://github.com/rich-murphey/kumodd/wiki/Log2Timeline-Export).

## User Guide
* [Overview](https://github.com/rich-murphey/kumodd/wiki/Home)
* [Usage Examples](https://github.com/rich-murphey/kumodd/wiki/How-to-Use-Kumodd)
* [How to Install](https://github.com/rich-murphey/kumodd/wiki/How-to-Install)  
* [How to Configure](https://github.com/rich-murphey/kumodd/wiki/How-to-Configure)  
* [Default Configuration](https://github.com/rich-murphey/kumodd/wiki/Default-configuration)  
* [Google Drive Metadata](https://github.com/rich-murphey/kumodd/wiki/Metadata)  
* [How to Search for Files](https://github.com/rich-murphey/kumodd/wiki/Search-Query)  
* [Data Verification Methods](https://github.com/rich-murphey/kumodd/wiki/Methods)  
* [How to Verify Files](https://github.com/rich-murphey/kumodd/wiki/How-to-Verify-Data)  
* [Log2Timeline Export](https://github.com/rich-murphey/kumodd/wiki/Log2Timeline-Export)
* [Command Line Options](https://github.com/rich-murphey/kumodd/wiki/Command-line-options)  
* [How to Test Kumodd](https://github.com/rich-murphey/kumodd/wiki/How-to-Test-Kumodd)  
* [How to Build](https://github.com/rich-murphey/kumodd/wiki/How-to-Build)  
* [Example Metadata](https://github.com/rich-murphey/kumodd/wiki/Example-Metadata)  
* [Limitations](https://github.com/rich-murphey/kumodd/wiki/Limitations)  
* [References](https://github.com/rich-murphey/kumodd/wiki/References)  
