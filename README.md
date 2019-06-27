# kumodd

Google Drive is the only supported cloud service currently.

### Setup

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
    1. Click "create".  A dialog "OAuth client will pop up.  Click OK.
    1.  Under "Oauth 2.0 client IDs", to the far right of the new ID, is a down arrow icon. Click the down arrow icon to download it.
    1. Rename it to gdrive.json, and move it to the config directory inside the kumodd directory created in step 1.

1. Authorize kumodd to access the cloud account:

    When kumodd is used for the first time to connect to a cloud service:
    ```
    python3 kumod.py -l all
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

    To force kumodd to not use a local web browser, invoke it with the `--noauth_local_webserver` option:
    ```
    python3 kumodd.py --noauth_local_webserver -l all
    ```

### Usage

`python3 kumodd.py -s [service] [action] [filter]`

**[service]**

The type of cloud service being accessed.  The default service is Google Drive, which is the only service supported currently.

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

`python3 kumodd.py -l all`

List only images stored in the service: 

`python3 kumodd.py -l image`

Download only PDF files and save the in the Desktop folder:

`python3 kumodd.py -d all -l /home/user/Desktop/`

Download files from Google Drive using files listed in a CSV file stored in /home/user/Desktop/

`python3 kumodd.py -csv /home/user/Desktop/gdrive_list.csv`

To relay HTTP though a proxy, specify the proxy in config/config.cfg.

    ```
    [proxy]
    host = proxy.host.com
    port = 8888
    user = username (optional)
    pass = password (optional)
    ```

The default config file is config/config.dat.  To select an alternate config file, use the `-c` option:

`python3 kumodd.py -c config/alternate.dat`

At the time of writing (June 2019), the following default API limits are imposed by [Google Cloud Platform Quotas](https://console.cloud.google.com/apis/api/drive.googleapis.com/quotas).

- 1,000,000,000 queries per day
- 1,000 queries per 100 seconds per user
- 10,000 queries per 100 seconds
