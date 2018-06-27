# Installation Guide


## Environment

So far `gmail2maildir` has only been tested on RHEL 7.  Other OSes
to be supported later.

The `gmail2maildir` tool requires the following packages for RHEL 7
to be installed:

```
python-pathlib
python2-google-api-client
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

1.  Select "Create a project" and click "Continue".

    It will take a few moments, but you will be taken to a page
    saying "The API is enabled".

1. Click "Go to credentials".

1. On the "Add credentials to your project" page, click "Cancel".

1. On the "Credentials" page, select the "OAuth consent screen" tab.

   * Select an email address.

   * For "Product name shown to users", enter "gmail2maildir".

   * Click "Save"

1. Select the "Credentials" tab (if not already returned to that tab).

1. Select the "Create Credentials" button and select "OAuth client ID".

1. Select "Other", enter "gmail2maildir" for name, then click "Create".

1. To dismiss the "OAuth client" window, click on "OK".

   You should now see your "gmail2maildir" OAuth 2.0 client ID listed.

1. Select the download icon to the far right of the entry.  Download the
   file and call it `client_secret.json`.

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

Running the tool should open a browser window asking you to "Choose
an account".  Select your @oath.com account and on the next page
click on the "ALLOW" botton.

Back on the shell running `gmail2maildir`, you should see the message
"Authentication successful." and the tool exits.  You should now have
the `~/.config/gmail2maildir/credentials.json` file created.
