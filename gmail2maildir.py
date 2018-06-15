#! /usr/bin/python
#
# Can't use python3 since no google api client python package available for it.
#

"""
Download gmail messages tagged with a label into a Maildir directory.
"""

from __future__ import print_function

import sys
import os
import errno
import base64
import email

from pathlib import Path, PurePath
from optparse import OptionParser
from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# Can't use exist_ok arg for Path.mkdir.  Only added in v3.
def mkdir_exists_ok(path, mode, parents):
    try:
        path.mkdir(mode, parents)
    except OSError as e:
	if e.errno == errno.EEXIST:
	    pass
	else:
	    exit("mkdir of '%s' failed." % path)


def SetupOptionParser(app_config_dir, maildir_path):
    # Usage message is the module's docstring.
    parser = OptionParser(usage=__doc__)

    parser.add_option('--label',
                    default='dnl',
                    dest='download_label_name',
                    help="label used to identify mails to download")
    parser.add_option('--keep-label',
                    default=False,
                    action='store_true',
                    dest='keep_label',
                    help="don't remove label from mail after download")
    parser.add_option('--archive-mail',
                    default=False,
                    action='store_true',
                    dest='archive_mail',
                    help="archive mail after download")
    parser.add_option('--maildir',
                    default=maildir_path,
                    dest='maildir',
                    help="path to directory in maildir format")
    parser.add_option('--client-secret',
                    default=app_config_dir / 'client_secret.json',
                    dest='client_secret_file',
                    help="Client_secret file")
    parser.add_option('--credentials',
                    default=app_config_dir / 'credentials.json',
                    dest='credentials_file',
                    help="credentials file")
    parser.add_option('--user-id',
                    default='me',
                    dest='user_id',
                    help="user id's mail to download")
    return parser


def RequireOptions(options, *args):
    missing = [arg for arg in args if getattr(options, arg) is None]
    if missing:
        exit('Missing options: %s' % ' '.join(missing))


def gmail_api_setup(scope, client_secret_file, credentials_file):
    store = file.Storage(str(credentials_file))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(str(client_secret_file), scope)
        creds = tools.run_flow(flow, store)
    return build('gmail', 'v1', http=creds.authorize(Http()))


def main(argv):
    home_env = os.getenv('HOME')

    if home_env:
        home = Path(home_env)
        app_config_dir = home / '.config' / 'gmail2maildir'
    else:
        app_config_dir = PurePath('')

    maildir_env = os.getenv('MAILDIR')

    if maildir_env:
        maildir_path = Path(maildir_env)
    else:
        if home_env:
            maildir_path = home / 'Mail' / 'Inbox'
        else:
            maildir_path = PurePath('')

    options_parser = SetupOptionParser(app_config_dir, maildir_path)
    (options, args) = options_parser.parse_args()

    maildir_tmp = options.maildir / 'tmp'
    maildir_new = options.maildir / 'new'
    maildir_cur = options.maildir / 'cur'

    mkdir_exists_ok(maildir_tmp, 0o700, True)
    mkdir_exists_ok(maildir_new, 0o700, True)
    mkdir_exists_ok(maildir_cur, 0o700, True)

#    if options.refresh_token:
#        RequireOptions(options, 'client_id', 'client_secret')

#    print('app_config_path = %s' % app_config_dir)
#    print('maildir_top = %s' % options.maildir)
#    print('credentials_file = %s' % options.credentials_file)
#    print('client_secret_file = %s' % options.client_secret_file)
#    print('maildir_tmp = %s' % maildir_tmp)
#    print('maildir_new = %s' % maildir_new)
#    exit(0)

    #
    # Setup the Gmail services for readonly and read/write access methods.
    # Do modify first so that when the gAPI opens a browser connection to
    # prompt the user, it's for a modify access request.
    #

    gapi_url = 'https://www.googleapis.com/auth/'
    service_mod = gmail_api_setup(gapi_url + 'gmail.modify',
                        options.client_secret_file, options.credentials_file)
    service_ro  = gmail_api_setup(gapi_url + 'gmail.readonly',
                        options.client_secret_file, options.credentials_file)

    #
    # Find our special download label.
    #

    results = service_ro.users().labels().list(userId=options.user_id).execute()
    labels = results.get('labels', [])

    try:
        download_label_id = \
            next(x for x in labels \
		if x['name'] == options.download_label_name)['id']
    except StopIteration as err:
        exit("Could not find download label '%s'." % \
	        options.download_label_name)

    #
    # Find all mails with the download label.
    #

    # Should I select messages with the label only if they're in INBOX?
    results = service_ro.users().messages().list(userId=options.user_id,\
        labelIds=[download_label_id],maxResults=500).execute()

    messages = results.get('messages', [])

    if not messages:
        print("No messages found with label '%s'." % \
	        options.download_label_name)
        exit(0)

    #exit(0)

    #
    # Download mails with the download label and remove the label from the mail.
    #

    for msg in messages:
        msg_id = msg.get('id')

        mailfn = Path(options.user_id + "_" + msg_id)
        mailfn_tmp = maildir_tmp / mailfn
        mailfn_new = maildir_new / mailfn

        msg = service_ro.users().messages().get(userId=options.user_id,\
	        id=msg_id,format='raw').execute()

        fo = open(str(mailfn_tmp), "wx")
        fo.write(base64.urlsafe_b64decode(\
	        msg['raw'].encode('ASCII')).replace('\r', ''))
        fo.close()
        mailfn_tmp.rename(mailfn_new)

	rlabels = []
	if options.archive_mail:
	    rlabels += ['INBOX']

	if not options.keep_label:
	    rlabels += [download_label_id]

	if rlabels:
	    upd_body = {'removeLabelIds': rlabels, 'addLabelIds': []}
            service_mod.users().messages().modify(userId=options.user_id,\
	            id=msg_id, body=upd_body).execute()


if __name__ == '__main__':
    main(sys.argv)
