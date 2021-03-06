The `gmail2maildir` tool will download mail from a gmail account into
[Maildir](https://en.wikipedia.org/wiki/Maildir) format.

After the `gmail2maildir` tool is installed \(see
[INSTALL.md](INSTALL.md)\), you can enter `gmail2maildir --help` to
see the available options.

The tool works by finding mails with a label, downloading those
emails, then removing the label when the download is successful.
The default label is `_dnl_`.

The downloaded emails will be placed into a Maildir directory
hierarchy specified by the `--maildir=MAILDIR` option.  If none is
specified, the tool looks for the `MAILDIR` environment variable.
If the variable isn't set, the default is `~/Mail/Inbox`.

If you'd like to have new mails automatically selected for
downloading, just create a rule to apply the label the tool searches
for.  Go to your gmail account and select "Settings" under the gear
icon.  Select the "Filters and Blocked Addresses" tab then click on
"Create a new filter" link.  In the "From" box, enter something like
`-(slkdjflksjdfksdjflkdsjfl@foobar.com)` then click "Create filter
with this search".  The idea is to create a negative filter for a
garbage address string which will hopefully never be matched.

On the next page, check "Apply the label".  Select "Choose label..."
then "New label".  In the "Please enter a new label name:", enter
`_dnl_` then click "Create".

Running `gmail2maildir` will only download the labeled mails and
exit.  If you'd like the tool to keep running and downloading, use
the `--poll` option with a number of seconds to wait between polls.
