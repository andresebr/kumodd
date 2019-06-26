# kumodd

Google Drive is currently supported. Other services coming soon.

### Setup

1. Install required packages for Python 3

   `pip3 install --user --upgrade absl-py`
   `pip3 install --user --upgrade google-api-python-client`
   `pip3 install --user --upgrade oauth2client`
   `pip3 install --user --upgrade socksipy-branch`

2. Create a new project in the [Google API Console](https://console.cloud.google.com/projectcreate). Use localhost as the redirect URI in the project configuration step. Once the project is created, a Client ID and Client secret will be generated.

3. Update `client_scret` and `secret_id` fields in `config/gdrive_config.json` with the credentials obtained in the previous step.

### Account authentication

When kumodd is used for the first time to connect to a cloud service, the respective driver will initiate the authorization process which requires the user to provide access credentials (user/password) for the account to be analyzed. The tool provides the user with a URL that needs to be opened in a web browser where the standard authentication interface for the service will request the account username and password.  If the authentication is successful, the provided access token is cached persistently in a `.dat` file saved under `/config` with the name of the service. Future requests will use the generated token and will not prompt the user for credentials again until the token expires or the generated file is deleted.


### Usage

`python3 kumodd.py -s [service] [action] [filter]`

**[service]**

The type of cloud service being accessed (only Google Drive is supported at the moment): 

`gdrive` Google Drive

**[action]**

The action to be performed using the selected service:

`-l` List files stored in an account drive as a plain text table.

`-d` Download files stored in an account drive in an specified location. 

`-csv` Use a CSV file to specify which files to download.

**[filter]**

The filter parameter specifies the subset of files to be listed/downloaded based on file type: 

`all` All files stored in the account

`doc` .doc, .docx, .odf files

`xls` spreadsheets

`ppt` presentation files

`text` text/source code files

`pdf` PDF files

`officedocs` All document, spreadsheet and presentation files

`image` images files

`audio` audio files

`video` video files

`<file>` Used with `-csv` action: CSV file containing the files to be downloaded.

`-p <path>` Used with `-d` and `-csv` action: Specify a path where the files will be downloaded.

### Usage examples

List all files stored in a Google Drive account:

`python3 kumodd.py -s gdrive -l all`

List only images stored in the service: 

`python3 kumodd.py -s gdrive -l image`

Download only PDF files and save the in the Desktop folder:

`python3 kumodd.py -s gdrive -d all -l /home/user/Desktop/`

Download files from Google Drive using files listed in a CSV file stored in /home/user/Desktop/

`python3 kumodd.py -s gdrive -csv /home/user/Desktop/gdrive_list.csv`

To relay HTTP though a proxy, specify the proxy in config/config.cfg:

    [proxy]
    host = proxy.host.com
    port = 8888
    user = username (optional)
    pass = password (optional)

To use kumodd without local web browser, invoke it with the --noauth_local_webserver
option:

`python3 kumodd.py --noauth_local_webserver -s gdrive -l all`

- Kumod will print the URL.
- Paste the URL into a browser, and complete the web login to obtain a token.
- Paste the token into kumodd.
- Then, kumodd is configured to access the specified google drive account.
