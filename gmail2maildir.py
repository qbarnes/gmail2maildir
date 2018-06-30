#! /usr/bin/env python2
#
# Copyright 2018 Quentin Barnes
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Can't use python3 since no google api client python package available for it.
#

"""
Download gmail messages tagged with a label into a Maildir directory.
"""

from __future__ import print_function

import sys
import os
import signal
import errno
import base64
import time
import argparse
import email

from pathlib import Path, PurePath
from apiclient import errors
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


Signal = 0

# For SIGHUP, we use it to get out of syscalls and then ignore it.
def sig_handle_hup(signum, frame):
    global Signal
    Signal = signum

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


Verbose = False

def verbose_eprint(*args, **kwargs):
    global Verbose
    if Verbose:
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


def SetupArgParser(app_config_dir, maildir_path):
    # Usage message is the module's docstring.
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-a', '--archive-mail',
                        default=False,
                        action='store_true',
                        dest='archive_mail',
                        help="archive mail after download")
    parser.add_argument('-c', '--credentials',
                        default=app_config_dir / 'credentials.json',
                        dest='credentials_file',
                        help="credentials file")
    parser.add_argument('-k', '--keep-label',
                        default=False,
                        action='store_true',
                        dest='keep_label',
                        help="don't remove label from mail after download")
    parser.add_argument('-l', '--label',
                        default='_dnl_',
                        dest='label_name',
                        help="label used to identify mails to download")
    parser.add_argument('-p', '--poll',
                        type=float,
                        dest='poll',
                        help="seconds between polling gmail for mail")
    parser.add_argument('-s', '--client-secret',
                        default=app_config_dir / 'client_secret.json',
                        dest='client_secret_file',
                        help="Client_secret file")
    parser.add_argument('-u', '--user-id',
                        default='me',
                        dest='user_id',
                        help="user id's mail to download")
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        dest='verbose',
                        help="enable verbose messages")
    parser.add_argument('maildir',
                        nargs=1,
                        type=Path,
                        default=maildir_path,
                        help="path to directory in maildir format")
    return parser


def gmail_api_setup(scope, client_secret_file, credentials_file):
    store = file.Storage(str(credentials_file))
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(str(client_secret_file), scope)
        creds = tools.run_flow(flow, store)
    return build('gmail', 'v1', http=creds.authorize(Http()))


def gmail2maildir(args):
    #
    # Setup the Gmail services for readonly and read/write access methods.
    # Do modify first so that when the gAPI opens a browser connection to
    # prompt the user, it's for a modify access request.
    #

    gapi_url = 'https://www.googleapis.com/auth/'
    service_mod = gmail_api_setup(gapi_url + 'gmail.modify',
                        args.client_secret_file, args.credentials_file)
    service_ro  = gmail_api_setup(gapi_url + 'gmail.readonly',
                        args.client_secret_file, args.credentials_file)

    #
    # Find our special download label.
    #

    results = service_ro.users().labels().list(userId=args.user_id).execute()
    labels = results.get('labels', [])

    try:
        download_label_id = \
            next(x for x in labels \
                if x['name'] == args.label_name)['id']
    except StopIteration as err:
        exit("Could not find download label '%s'." % \
                args.label_name)

    #
    # Find all mails with the download label.
    #

    # Should I select messages with the label only if they're in INBOX?
    results = service_ro.users().messages().list(userId=args.user_id,\
        labelIds=[download_label_id],maxResults=500).execute()

    messages = results.get('messages', [])

#    if not messages:
#        print("No messages found with label '%s'." % \
#                args.label_name)
#        exit(0)

    #exit(0)

    #
    # Download mails with the download label and remove the label from the mail.
    #

    maildir_tmp = args.maildir[0] / 'tmp'
    maildir_new = args.maildir[0] / 'new'

    for msg in messages:
        msg_id = msg.get('id')

        mailfn = Path(args.user_id + "_" + msg_id)
        mailfn_tmp = maildir_tmp / mailfn
        mailfn_new = maildir_new / mailfn

        msg = service_ro.users().messages().get(userId=args.user_id,\
                id=msg_id,format='raw').execute()

        fo = open(str(mailfn_tmp), "wx")
        fo.write(base64.urlsafe_b64decode(\
                msg['raw'].encode('ASCII')).replace('\r', ''))
        fo.close()
        mailfn_tmp.rename(mailfn_new)

        rlabels = []
        if args.archive_mail:
            rlabels += ['INBOX']

        if not args.keep_label:
            rlabels += [download_label_id]

        if rlabels:
            upd_body = {'removeLabelIds': rlabels, 'addLabelIds': []}
            service_mod.users().messages().modify(userId=args.user_id,\
                    id=msg_id, body=upd_body).execute()

    return len(messages)


def main(argv):
    global Signal
    global Verbose

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

    parser = SetupArgParser(app_config_dir, maildir_path)
    args = parser.parse_args()

    Verbose = args.verbose

    maildir_tmp = args.maildir[0] / 'tmp'
    maildir_new = args.maildir[0] / 'new'
    maildir_cur = args.maildir[0] / 'cur'

    mkdir_exists_ok(maildir_tmp, 0o700, True)
    mkdir_exists_ok(maildir_new, 0o700, True)
    mkdir_exists_ok(maildir_cur, 0o700, True)

#    print('app_config_path = %s' % app_config_dir)
#    print('maildir_top = %s' % args.maildir)
#    print('credentials_file = %s' % args.credentials_file)
#    print('client_secret_file = %s' % args.client_secret_file)
#    print('maildir_tmp = %s' % maildir_tmp)
#    print('maildir_new = %s' % maildir_new)
#    exit(0)

    if args.poll:
        if args.poll <= 0:
            exit("poll parameter must be greater than 0.")

        signal.signal(signal.SIGHUP, sig_handle_hup)

        t_start = time.time()
        while True:
            try:
                verbose_eprint("polling...")
                msg_cnt = gmail2maildir(args)
                if msg_cnt:
                    verbose_eprint("downloaded %d messages." % msg_cnt)
                sleep_time = max(0, args.poll - (time.time() - t_start))
                verbose_eprint("sleeping for %f seconds." % sleep_time)
                time.sleep(sleep_time)
                if Signal == 0:
                    t_start += args.poll
                else:
                    t_start = time.time()
                    Signal = 0
            except KeyboardInterrupt:
                break
    else:
        gmail2maildir(args)

if __name__ == '__main__':
    main(sys.argv)
