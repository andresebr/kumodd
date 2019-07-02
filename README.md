# kumodd

Kumodd downloads selected files and/or meta-data from a specified Google Drive
account. Default meta-data include the File ID, path and number of revisions. The MD5
digest is included only for file types that are not native to google docs, such as MS
Office, as shown below.

``` shell
./kumodd.py -l doc
Working...
INDEX FILE ID                                       REMOTE PATH                   REVISION   HASH(MD5)           
    0 1BK0I0ScYsZPembZdG9B9qBgtXV5WpyJ3JY31W-9ldo8  My Drive/Untitled document    3          -                   
    1 0B7pAT_44h5smSGVkcjywyudk78bs9789sboeuyt2tro  My Drive/notes.docx           1          1376e9bf5fb781c3e428356b4b9aa21c
    2 0B7pAT_44h5sbs897bsmazZorexlchm0wu90sgzrlu9h  My Drive/Letter to John.docx  1          4cb0b987cb879d48f56e4fd2cfd57d83
    3 13qAT9ARVaCbGKmCXiN_60XnCAyE5ZrXz_4uKRjaE3mU  My Drive/Todo List            27         -                   
```

## Setup

To setup kumodd, 1) install kumodd and requirements, 2) obtain a Google Oauth
client ID, and 3) authorize access to a specified cloud account.

1. Download kumodd and install the required packages.
    ```
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python3 -m pip install --user -r requirements.txt
    ```

1. Obtain a Google Oauth client ID:
    1. If you do not have a free google cloud account, create one as described in [Create a new billing account](
https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account).  
    1. Login to your [Google cloud account](https://console.cloud.google.com)
    1. Create a project: [Create Project](https://console.cloud.google.com/projectcreate).
    1. Then create API credentials. Select APIs & Services, then Credentials, or go to: [Credentials](https://console.cloud.google.com/apis/credentials).
    1. Click "Create Credentials" and select "Oauth client ID".
    1. Select the radio button "Web Application".
    1. In "Authorized redirect URIs", enter: `http://localhost:8080`
    1. Click "create".  A dialog "OAuth client" will pop up.  Click OK.
    1.  Under "Oauth 2.0 client IDs", to the far right of the new ID, is a down arrow icon. Click the down arrow icon to download it.
    1. Rename it to gdrive.json, and move it to the config directory inside
       the kumodd directory created in step 1: kumodd/config/gdrive.json.

1. Authorize kumodd to access the cloud account:

    When kumodd is used for the first time to connect to a cloud service:
    ```
    python3 kumodd.py -l all
    ```

    Kumodd will open a web browser to the login page of the cloud service (e.g. google
    drive). 
    1. Login to the cloud account. After logging in, the page will request approval for the web service to access the cloud account.  
    1. Approve the access. Then, kumodd stores the access credentials in the config directory.  
    
    If there is no local browser, kumod will instead print a URL for the login page of
    the cloud service. 
    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  It will ask for approval of the web app.
    1. Click "Approve". After clicking approve, the web page will show an access token.  Kumodd will be waiting for input. 
    1. Copy and paste that token into kumodd and press enter. Kumod then saves the
    token in config/gdrive.dat, for later use.

    Later use of kumodd will not prompt for login details again until the token expires
    or the generated file is deleted.

    To force kumodd to ignore a local web browser, and instead print the URL, invoke it with the `--noauth_local_webserver` option:
    ```
    python3 kumodd.py --noauth_local_webserver -l all
    ```

## Usage

`python3 kumodd.py [-s service] [action] [filter]`

**[service]**

    Select the cloud service.

    `-s gdrive` access a Google Drive account. This is the default service.

**[action]**

    The action to be performed using the selected service:

    `-l` List files stored in an account drive as a plain text table.

    `-d` download files stored in an account.

    `-csv <file>` specifies a CSV file containing a list of selected files.

    `-p <path>` specifies a path where the files will be downloaded.

**[filter]**

    The filter parameter limits access to a selected category of files:

Filter	| Description 
:------	| :-----------
all	| All files stored in the account
doc	| .doc, .docx, and .odf files
xls	| Spreadsheets
ppt	| Presentation files
text	| Text/source code files
pdf	| PDF files
officedocs	| All document, spreadsheet and presentation files
image	| Image files
audio	| Audio files
video	| Video files


## Usage examples

List all files stored in a Google Drive account:

`python3 kumodd.py -l all`

List only images stored in Google Drive:

`python3 kumodd.py -l image`

Download all PDF files and save them in the Desktop folder:

`python3 kumodd.py -d pdf -p /home/user/Desktop/`

Download selected files listed in the file, gdrive_list.csv.

`python3 kumodd.py -csv /home/user/Desktop/gdrive_list.csv`

To relay kumodd access though an HTTP proxy, specify the proxy in config/config.cfg:
```
[proxy]
host = proxy.host.com
port = 8888
user = username (optional)
pass = password (optional)
```

The default config file is config/config.dat.  To select an alternate config file, use the `-c` option:

`python3 kumodd.py -c config/alternate.dat`

## Notes

To use kumod on windows, add python and git to the PATH environment variable, and then
do the rest of the setup.

``` shell
SET "PATH=%PATH%;C:\Python37"
SET "PATH=%PATH%;C:\ProgramFile\Git\bin"
git clone https://github.com/rich-murphey/kumodd.git
cd kumodd
python -m pip install --user -r requirements.txt
.\kumodd.py -l doc
```

Using an HTTP proxy on Windows does not work due to unresolved issues with httplib2.

At the time of writing (June 2019), the following default API limits are imposed by [Google Cloud Platform Quotas](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas).

- 1,000,000,000 queries per day
- 1,000 queries per 100 seconds per user
- 10,000 queries per 100 seconds

kumodd uses the [Google API Python
Client](https://github.com/googleapis/google-api-python-client) which is officially
supported by Google; It is feature complete and stable; hosever, it is not actively
developed.  It has has been replaced by the [Google Cloud client
libraries](https://github.com/googleapis/google-cloud-python) which are in development,
and preferred for new work.

