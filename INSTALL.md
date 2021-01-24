# Installation Guide


## Environment

The `gmail2maildir` tool has been tested on CentOS/RHEL 7 & 8 and on
Fedora 33.  If you have suggestions for supporting other OSes, please
file a pull request.

The `gmail2maildir` tool requires the following packages to be
installed for Fedora 33:
```
   python3
   python3-google-api-client
```


For RHEL/CentOS 8, use
[EPEL](https://fedoraproject.org/wiki/EPEL) and install:
```
   python3
   python3-google-api-client
```
(Note: RHEL 8 instructions incomplete and untested, possibly
due to EPEL module trouble.)


For RHEL/CentOS 7, use
[EPEL](https://fedoraproject.org/wiki/EPEL) and install:
```
   python3
   python36-google-api-client
```


## Creating the `client_secret.json` file

Once dependencies have been resolved, the second step is to create
the `~/.config/gmail2maildir/client_secret.json` file.  This
step only has to be done once.  The file may also be copied around
to other hosts as needed.

Note you do not have to do these steps to create the
`client_secret.json` file on the host you intend to run
`gmail2maildir` on to download your mail.  However, it's then up to
you to copy the file over to the target host.

To create the `client_secret.json` file:

1. Go to the page [Enable an API](https://console.developers.google.com/flows/enableapi?apiid=gmail).

1. If necessary, agree to Terms of Service, set Country of residence,
   and click "Agree and continue".

1. Select "Create a project" and click "Continue".

    It will take a few moments, but you will be taken to a page
    saying "The API is enabled".

1. Click "Go to credentials".

1. On the "Credentials - Add credentials to your project" page, click "Cancel".

1. On the left column, select the "OAuth consent screen".

   1. On the "OAuth consent screen":

      * For User Type select "External".

      * Click "CREATE".

   1. On the "Edit app registration" page:

      1. On step "OAuth Consent Screen":

         1. Under "App information":

            * For "App name", enter "gmail2maildir".

            * For "User support email" select your email address.

            * Leave "App logo" unchanged.

         1. Under "App domain":

            * Leave all fields blank.

         1. Under "Developer contact information"

           * For "Email addresses", enter your email address.

         1. Click "SAVE AND CONTINUE".

      1. On step "Scopes":

        1. Click "ADD OR REMOVE SCOPES".

        1. Under "Update selected scopes", add:

            * "../auth/gmail.modify"

            * "../auth/gmail.readonly"

            * Click "UPDATE"

      1. Click "SAVE AND CONTINUE".

   1. On step "Test users":

      * Click on "ADD USERS"

	 * On the "Add users" panel, and add your own email.

	 * Click "ADD".

      * Click "SAVE AND CONTINUE".

      * Click "BACK TO DASHBOARD".

1. On the left column, select the "Credentials" tab.

   1. Select the "Create Credentials" button and select from the drop-down
      "OAuth client ID".

      * On the "Create OAuth client ID" page, for "Application type", select
        "Desktop app".

      * For "Name" enter "gmail2maildir".

      * Click "CREATE".

   1. Dismiss the "OAuth client created" window by clicking "OK".

      * You should now see your "gmail2maildir" OAuth 2.0 client ID listed.

   1. Select the download icon to the far right of the entry.  Download the
      file and rename it to `client_secret.json`.

You should now have your `client_secret.json` file.  Its contents will
look something like this:

```
{"installed":{"client_id":"834010465788-dje8nr45h6zp450se4ttd69a36j1kk92.apps.googleusercontent.com","project_id":"optimum-purple-208301","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"wT7Vsj7jBBG9Ql0qf1H7MZQ4","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}
```

Now type:

```
   $ mkdir -p ~/.config/gmail2maildir
   $ cp -p client_secret.json ~/.config/gmail2maildir
   $ chmod 0600 ~/.config/gmail2maildir/client_secret.json
```


## Creating the `credentials.json` file

The next step is to create the `~/.config/gmail2maildir/credentials.json`
file.  The `gmail2maildir` tool does the work for you.  For this
step, make sure you have a browser open on your desktop or laptop on
the same host you're running `gmail2maildir` on.  The tool will be
opening a window in the local browser.

Go to the gmail2maildir repo directory and type:

```
   $ make
   $ ./gmail2maildir
```

Running the tool should open one of two browser windows.

If you have multiple accounts, the first window will prompt you to
"Choose an account".  Select the account you will use with this tool
and continue to the directions for only having one account.

On the "Google hasn't verified this app" screen, click "Continue".

A popup window will describe access.  Click "Allow".

The next page will ask you to approve the tool's access to your
gmail account.  Click "Allow".

The last screen will say, "The authentication flow has completed."
You may now close the browser window.

Back on the shell running `gmail2maildir`, you should see the message
"Authentication successful." and the tool exits.  You should now have
the `~/.config/gmail2maildir/credentials.json` file created.

If you received the error message, "Could not find download label
'\_dnl\_'.", go back to your gmail session in your browser and create
the label.

