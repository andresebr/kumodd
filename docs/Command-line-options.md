    kumodd [flags]

### Kumodd General Options

    -p,--destination: Destination folder location
      (default: './download')
    -d,--download: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: Download files, optionally filter, and verify MD5 on disk
    --[no]l2t: generate log2timeline CSV files from cached metadata.
      (default: 'false')
    -l,--list: <all|doc|xls|ppt|text|pdf|office|image|audio|video|other>: List files in google drive and verify files on disk match MD5
    --log: <DEBUG|INFO|WARNING|ERROR|CRITICAL>: Set the level of logging detail.
      (default: 'ERROR')
    -m,--metadata_destination: Destination folder for metadata information
      (default: './download/metadata')
    -s,--service: <gdrive|dropbox|box|onedrive>: Service to use
      (default: 'gdrive')
    -csv,--usecsv: Download files listed in a previously generated CSV file, and verify MD5 of files on disk
      (a comma separated list)
    -V,--[no]verify: Verify files and metadata on disk match original MD5. Use local metadata. Do not connect to Google Drive.
      (default: 'false')
    --[no]version: Print version number and exit.
      (default: 'false')

The -d and -l options take a filter argument that selects a category of files.  A file's
category is determined its mime type.

Filter	| Description 
:------	| :-----------
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

### Google Drive Options

    --[no]browser: open a web browser to authorize access to the google drive account
      (default: 'true')
    -o,--col: column set defined under csv_columns in config.yml that specifies table and CSV format
      (default: 'normal')
    -c,--config: config file
      (default: 'config/config.yml')
    --corpora: Google Drive corpora
      (default: 'user')
    -f,--folder: source folder within Google Drive
    --gdrive_auth: Google Drive account authorization file.  Configured in config/config.yml if not specified on command line.
    --[no]pdf: Convert all native Google Apps files to PDF.
      (default: 'true')
    -q,--query: metadata query (filter)
    --[no]revisions: Download every revision of each file.
      (default: 'true')
    --scope: Google Drive scope
      (default: 'https://www.googleapis.com/auth/drive.readonly')
    --spaces: A comma-separated list of spaces to query within the corpus. Supported values are 'drive', 'appDataFolder' and 'photos'.
      (default: 'drive')

### Python Options

    -?,--[no]help: show this help
      (default: 'false')
    --[no]helpfull: show full help
      (default: 'false')
    --[no]helpshort: show this help
      (default: 'false')
    --[no]helpxml: like --helpfull, but generates XML output
      (default: 'false')
    --[no]only_check_args: Set to true to validate args and exit.
      (default: 'false')
    --[no]pdb_post_mortem: Set to true to handle uncaught exceptions with PDB post mortem.
      (default: 'false')
    --profile_file: Dump profile information to a file (for python -m pstats). Implies --run_with_profiling.
    --[no]run_with_pdb: Set to true for PDB debug mode
      (default: 'false')
    --[no]run_with_profiling: Set to true for profiling the script. Execution will be slower, and the output format might change over time.
      (default: 'false')
    --[no]use_cprofile_for_profiling: Use cProfile instead of the profile module for profiling. This has no effect unless --run_with_profiling is set.
      (default: 'true')

### Logging Options

    --[no]alsologtostderr: also log to stderr?
      (default: 'false')
    --log_dir: directory to write logfiles into
      (default: '')
    --[no]logtostderr: Should only log to stderr?
      (default: 'false')
    --[no]showprefixforinfo: If False, do not prepend prefix to info messages when it's logged to stderr, --verbosity is set to INFO level, and python logging is used.
      (default: 'true')
    --stderrthreshold: log messages at this level, or more severe, to stderr in addition to the logfile.  Possible values are 'debug', 'info', 'warning', 'error', and 'fatal'.  Obsoletes
      --alsologtostderr. Using --alsologtostderr cancels the effect of this flag. Please also note that this flag is subject to --verbosity and requires logfile not be stderr.
      (default: 'fatal')
    -v,--verbosity: Logging verbosity level. Messages logged at this level or lower will be included. Set to 1 for debug logging. If the flag was not set or supplied, the value will be changed
      from the default of -1 (warning) to 0 (info) after flags are parsed.
      (default: '-1')
      (an integer)
    
Use 'kumodd --helpfull' to get a list of all flags.
    
    
