# Installing Kumodd

Kumodd is a command line utility.

## How to Install Kmodd on Windows

To install Kumodd on Windows, download kumodd.exe from the [kumodd release
page](https://github.com/rich-murphey/kumodd/releases/).  Note that the 'Source code'
files are not required.  kumodd.exe is a standalone windows command line utility.


Next, move kumodd.exe to C:\Windows.  Moving it to C:\Windows will ensure it is in the
default path, and as a result, is avialable on the command line in a CMD or powershell
window.

Then, open a cmd shell or powershell, and run it.

    kumodd --helpfull

## How to Install Kmodd on Unix

To setup kumodd, install python 3 and git, then install kumodd and its requirements.

On Debian or Ubuntu:

    apt install python3 git diff
    git clone https://github.com/rich-murphey/kumodd.git
    cd kumodd
    python3 -m pip install --user -r requirements.txt
    kumodd --helpfull

## Setup Kmodd on Windows or Unix

To access Google Drive, Kumodd requires two credential files:

      config/google_api_permission.json - permission to access the Google API
      config/google_drive_account_permission.json - permission to access a user's Google Drive account

Step 1) Obtain google_api_permission.json (permission to access the Google API):


    1. [Create a free google cloud account](https://cloud.google.com/billing/docs/how-to/manage-billing-account#create_a_new_billing_account).  
    1. [Login to your Google cloud account](https://console.cloud.google.com).
    1. [Create a Project](https://console.cloud.google.com/projectcreate).
    1. [Create Oauth2 API credential for the
       project](https://console.cloud.google.com/apis/credentials).
    1. Click "Create Credentials" and select "Oauth client ID".
    1. Select the radio button "Web Application".
    1. In "Authorized redirect URIs", enter: http://localhost:8080
    1. Click "create".  Next, a dialog "OAuth client" will pop up.
    1. Click OK.  Next, it will show the list of "Oauth 2.0 client IDs".
    1. Click the down arrow icon at far right of the new ID.  The ID will download.
    1. Copy the downloaded ID it to kumodd/config/gdrive.json.

Step 2) Obtain google_drive_account_permission.json (permission to access a specific user's Google Drive account):

The first time kumodd is used (e.g. __kumodd -list all__), kumodd will open the Google
Drive login page in a browser.


    1. Login to the cloud account. Next, it will request approval.
    1. Click "Approve". Next, kumodd stores the Oauth token in config/gdrive.dat.

If there is no local browser, or if --nobrowser is used, kumodd will
instead print a URL of the login page.


    1. Copy the URL and paste it into a browser.  
    1. Login to the cloud account.  Next, it will request approval.
    1. Click "Approve". Next, the page will show an access token.
    1. Copy the token from the web page. Paste it into kumodd, and press enter. Next, kumodd saves the Oauth token in config/gdrive.dat.

Once authorized, the login page will not be shown again unless the token
expires or config/gdrive.dat is deleted.

