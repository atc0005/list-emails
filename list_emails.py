#!/usr/bin/env python3

# https://github.com/atc0005/list-emails

# Purpose: Generate lists of emails within specified folders and accounts

# See docs/references.md for resources used during development of this script




########################################################
# Modules
########################################################

import argparse
import configparser
import datetime
import email.parser
import email.policy
import imaplib
import json
import logging
import logging.handlers
import os
import pprint
import sys


#######################################################
# CONSTANTS - Modify INI config files instead
#######################################################

script_path = os.path.dirname(os.path.realpath(__file__))

# The name of this script used (as needed) by error/debug messages
script_name = os.path.basename(sys.argv[0])

DATE = datetime.date.today()
TIME = datetime.datetime.now().time()
TODAY = DATE.strftime('%Y-%m-%d')
NOW = TIME.strftime('%H_%M')
TIMESTAMP = "{}-{}".format(TODAY, NOW)

app_name = 'ls-emails'

# The configuration file should be found in the same directory as this script
config_file = os.path.join(script_path, 'accounts.ini')

output_file_header_template = os.path.join(
    script_path, 'templates', 'email_list_header.tmpl')

# Location where this script will write lists of emails
output_dir = os.path.join(script_path, 'output')
log_dir = os.path.join(script_path, 'log')

app_log_file = os.path.join(log_dir, "{}-{}.txt".format(app_name, TIMESTAMP))

file_formatter = logging.Formatter('%(asctime)s - %(name)s - L%(lineno)d - %(funcName)s - %(levelname)s - %(message)s')
stdout_formatter = logging.Formatter('%(asctime)s - %(funcName)s - %(message)s')

# Grab root logger and set initial logging level. In our case, we are not
# restricting the log level at the root logger, but are instead applying
# appropriate restrictions at each handler.
root_logger = logging.getLogger()
root_logger.setLevel(logging.NOTSET)

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(stdout_formatter)
stdout_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    app_log_file, mode='w', delay=True, encoding='utf-8')
file_handler.setFormatter(file_formatter)
file_handler.setLevel(logging.DEBUG)

# Create logger object that inherits from root and will be inherited by
# all modules used by this project
app_logger = logging.getLogger(app_name)
app_logger.addHandler(stdout_handler)
app_logger.addHandler(file_handler)
app_logger.setLevel(logging.DEBUG)

# Create top-level logger object. We'll use this to note our progress with
# output to the console and to any configured log files
log = logging.getLogger(app_name).getChild(__name__)


# TODO: Import JSON configuration file listing email accounts, folders, passwords
# script_path = os.path.dirname(os.path.realpath(__file__))
# config_file = os.path.join(script_path, 'email_accounts.json')
# try:
#     config_file_fh = open(config_file)
# except Exception as error:
#     log.exception("Failed to open %s: %s", config_file, error)
#     sys.exit(1)
#
# config = json.load(config_file_fh.read())


########################################################
# Classes
########################################################


class EmailAccount(object):

    """An email account as described in the accounts.ini config file."""

    def __init__(self, config, account):

        self.log = log.getChild(self.__class__.__name__)

        self.settings = {}
        self.name = account

        try:
            for key, value in config.items(account):
                self.settings[key] = value

        except configparser.NoSectionError as error:
            self.log.exception(
                "Unable to parse options for '%s' section of config file: %s",
                account, error)
            raise


########################################################
# Functions
########################################################

def create_output_dirs(dir_list):
    """Create output directories for log files and for email list files"""

    # Use root logger since output log file directory may not exist yet;
    # attempting to use the module logger without the needed directory
    # will result in a FileNotFoundError exception

    for directory in dir_list:
        root_logger.info("Attempting to create directory: %s", directory)
        try:
            os.mkdir(directory)
        except FileExistsError as error:
            root_logger.info("%s directory already exists: %s.",
                directory, error)
            root_logger.debug("Moving on ...")
            continue
        else:
            root_logger.info("Successfully created directory: %s", directory)


def load_config(config_file):
    """Load configuration using provided config file"""

    log = logging.getLogger(app_name).getChild(__name__)

    log.debug("About to process config file: %s", config_file)

    parser = configparser.ConfigParser()
    processed_file = parser.read(config_file)

    if processed_file:
        log.debug("CONFIG: Config file loaded: %s",
            processed_file)
    else:
        log.error("Failure to read config file; "
            "See provided template, modify and place in the same directory"
            " as this script.")

        raise IOError("Failure to read config file; "
            "See provided template, modify and place in the same directory"
            " as this script.")

    return parser


def get_folder_count(email_address, mailbox, folder):
    """
    Receives: email address, open mailbox connection and folder name
    Returns: number of messages in a specified folder
    """

    log = logging.getLogger(app_name).getChild(__name__)

    log.debug("Checking message count in folder: %s", folder)

    # By this point we should have already confirmed that the folder exists
    # so now go ahead and try to get the number of emails in the folder
    #
    # This doesn't appear to catch invalid folder references, but it WILL
    # catch situations where a connection to the remote IMAP server has
    # timed out
    try:
        result, message_count = mailbox.select(mailbox=folder, readonly=True)
    except imaplib.IMAP4.error as error:
        log.exception("Unable to select %s to check contents (%s)",
            folder, error)
        sys.exit(error)

    # If the select method was able to list the folder ...
    if result == 'OK':

        # .. then the resulting message count is within the returned list
        message_count = int(message_count[0])

        return message_count

    # If the result code doesn't indicate success then the message count
    # is instead an error string
    else:
        log.error("%s: Unable to list messages in the %s folder: %s",
         email_address, folder, message_count)

        return imaplib.IMAP4.error(
            "%s: Unable to list messages in the %s folder: %s",
            email_address, folder, message_count)


# Intended for testing purposes, maybe used in some other way later on
def list_folder_count(email_address, mailbox, folder):

    """
    Receives: open mailbox connection, folder
    Returns: nothing
    Prints: various stats about messages within provided folder
    """

    log = logging.getLogger(app_name).getChild(__name__)

    try:
        message_count = get_folder_count(email_address, mailbox, folder)

    except imaplib.IMAP4.error as error:
        log.exception("Failed to list folder count: %s", error)
        raise

    else:
        log.debug("%d messages found in '%s'", message_count, folder)

    if message_count > 0:

        one_month_back_imap4_format = (datetime.date.today() - datetime.timedelta(365/12)).strftime("%d-%b-%Y")
        yesterday_imap4_format = (datetime.date.today() - datetime.timedelta(365/12/30)).strftime("%d-%b-%Y")
        today_imap4_format = datetime.date.today().strftime("%d-%b-%Y")

        _, messages_sent_today = mailbox.search(
            None, '(SENTON %s)' % today_imap4_format)
        log.info("%d messages sent today in %s",
            len(messages_sent_today[0].split()), folder)

        _, messages_sent_yesterday = mailbox.search(
            None, '(SENTON %s)' % yesterday_imap4_format)
        log.info("%d messages sent yesterday in %s",
            len(messages_sent_yesterday[0].split()), folder)

        _, messages_one_month_back = mailbox.search(
            None, '(BEFORE %s)' % one_month_back_imap4_format)
        log.info("%d messages sent prior to one month ago in %s",
            len(messages_one_month_back[0].split()), folder)

        _, messages_before_today = mailbox.search(
            None, '(BEFORE %s)' % today_imap4_format)
        log.info("%d messages sent before today in %s",
            len(messages_before_today[0].split()), folder)

        _, all_messages = mailbox.search(None, 'ALL')
        log.info("%d messages total in %s",
            len(all_messages[0].split()), folder)

    else:
        log.info("[-] No messages found in %s", folder)


def get_email_subject_lines(account, mailbox, folder):
    """Retrieve subject line from emails in specified folder"""

    email_subject_lines = []

    log.info("Searching %s for %s messages", folder,
        account.settings['search_criteria'])
    log.debug("Before search()")

    # Each command returns a tuple: (type, [data, ...]) where type is usually
    # 'OK' or 'NO', and data is either the text from the command response, or
    # mandated results from the command. Each data is either a string, or a
    # tuple. If a tuple, then the first part is the header of the response, and
    # the second part contains the data (ie: 'literal' value).
    result, data = mailbox.search(None, account.settings['search_criteria'])
    log.debug("After search()")
    log.debug("object as provided by repr(): %s", repr(data))

    # Select the messages wanted
    if result != 'OK':
        log.info("No messages. %s", result)
        exit()

    log.debug("Before looping over data[0]")

    # search() function returns a tuple made of:
    #
    # The search success status. A list made of a single, potentially very long
    # string of space-separated message numbers.
    for num in data[0].split():

        log.debug("Before fetch()")
        # For each selected message b'1 2 3 ...'
        (result, data) = mailbox.fetch(num, '(RFC822.HEADER)')
        log.debug("After fetch()")

        # Read it
        if result != 'OK':
            print("ERROR getting message", num, ", ", result)
            break

        log.debug("Using Parser() to retrieve headers")
        headers = email.parser.Parser(policy= email.policy.default).parsestr(
            data[0][1].decode("utf-8", "ignore"), headersonly=True)

        log.debug("Attempting to retrieve headers['subject'] value")
        subject = headers['subject']

        log.debug("Subject string value: %s", str(subject))
        log.debug("Subject type value: %r", type(subject))
        log.debug("Subject object properties: %s", dir(subject))

        # Remove 'Subject: ' from subject line and stray whitespace if present
        subject = subject.replace('Subject:', '').strip()

        email_subject_lines.append(subject)

    log.info("Finished searching %s for messages", folder)

    return email_subject_lines


def record_emails(output_file, items, header_template_file, account, folder, timestamp):
    """Record emails found in specified folder"""

    try:
        header_fh = open(header_template_file, "r")
    except IOError as error:
        log.exception("Failed to open %s: %s", output_file, error)

    # Attempt to reuse existing file
    try:
        output_fh = open(output_file, "a", encoding='utf-8')
    except Exception as error:
        log.exception("Failed to open %s: %s", output_file, error)

    header_template = header_fh.read()
    header = header_template.format(
        account=account.name,
        folder=folder,
        timestamp=timestamp
    )

    # Write out contents of header template as first entry in new file
    output_fh.write(header + '\n')

    items.sort()

    # Explicitly add trailing newline since we don't add them in other
    # functions or our templates.
    for line in items:
        log.debug("Writing: %r of type %s", line, type(line))
        output_fh.write(line + '\n')
    output_fh.write('\n')
    output_fh.close()


########################################################
# Main code body
########################################################

# This needs to be the first non-function bit of code executed prior to using
# logger objects with a file handler inherited from main app logger.
create_output_dirs(dir_list=[output_dir, log_dir])

log.debug("config file: %s", config_file)
log.debug("header template: %s", output_file_header_template)
log.debug("log file: %s", app_log_file)

config = load_config(config_file)

log.debug("Sections in config: %r", config.sections())
log.debug("%d sections in config file", len(config.sections()))

# Get list of email accounts; each account is listed in a separate section,
# so each section (not counting DEFAULT) is a separate account to check
for email_account in config.sections():

    account = EmailAccount(config, email_account)
    #pprint.pprint(account.settings)
    #sys.exit()

    list_of_emails_file = os.path.join(
        script_path, 'output', 'emails_for_{}-{}.txt'.format(account.name, TIMESTAMP))

    log.info("Checking folders for %s", account.name)

    # Create connection to IMAP server using explicit encryption
    log.debug("Attempting connection to %s on port %s...",
        account.settings['server_name'], account.settings['server_port'])
    try:
        mailbox = imaplib.IMAP4_SSL(
           account.settings['server_name'], account.settings['server_port'])
    except imaplib.IMAP4.error as error:
        log.exception("Unable to establish a connection to %s on %s/tcp (%s)",
            account.settings['server_name'], account.settings['server_port'],
            error)
        sys.exit(1)
    else:
        log.debug("Successfully connected to %s.",
            account.settings['server_name'])

    log.debug("Attempting to login to %s as %s",
        account.settings['server_name'], account.settings['username'])
    try:
        mailbox.login(account.settings['username'],
            account.settings['password'])
    except imaplib.IMAP4.error as error:
        log.exception("Unable to login to %s (%s)",
            account.settings['username'], error)
        sys.exit(1)
    else:
        log.debug("Successfully logged into %s as %s.",
            account.settings['server_name'],
            account.settings['username'])

    # Results in TypeError exception. May need to explicitly convert before
    # attempting to log/reference
    #log.debug("Full list of folders for %s: ", account.name, mailbox.list())

    folders = \
        [folder.strip() for folder in account.settings['folders'].split(',')]

    log.debug("Folders: %s", folders)

    for folder in folders:

        log.info("Examining %s folder for messages ...", folder)

        try:
            result, message_count = mailbox.select(mailbox=folder, readonly=True)
        except imaplib.IMAP4.error as error:
            log.exception("Unable to select %s to check contents (%s)",
                folder, error)
            sys.exit(error)

        # If the select method was able to list the folder ...
        if result == 'OK':

            # .. then the resulting message count is within the returned list
            message_count = int(message_count[0])

            if message_count >= 1:

                log.debug("message_count >=1")

                list_folder_count(account.name, mailbox, folder)

                log.debug("Getting email subject lines")

                emails_in_folder = get_email_subject_lines(
                    account, mailbox, folder)

                log.debug("About to try recording emails to %s",
                    list_of_emails_file)
                try:
                    record_emails(
                        os.path.join(output_dir, list_of_emails_file),
                        emails_in_folder,
                        output_file_header_template,
                        account,
                        folder,
                        TIMESTAMP)
                except (IOError, OSError) as error:
                    log.exception(
                        "%s: Unable to save list of emails for %s folder to %s",
                        account.name, folder, list_of_emails_file)
                    sys.exit()
            else:
                log.info("%d messages in %s folder", message_count, folder)


        # If the result code doesn't indicate success then the message count
        # is instead an error string
        else:
            log.error("%s: Unable to list messages in the %s folder: %s",
            account.name, folder, message_count)

        log.info("Finished examining %s folder for messages.", folder)

    # Close mailbox we were just looking at
    log.debug("Closing %s mailbox ...", account.name)
    try:
        mailbox.close()
    except imaplib.IMAP4.error as error:
        log.exception("Unable to close mailbox for %s (%s)",
            account.name, error)
        sys.exit(1)
    else:
        log.debug("Successfully closed %s mailbox", account.name)

    # Close connection to server after processing specified folders
    log.debug("Closing connection to %s ...", account.settings['server_name'])
    try:
        mailbox.logout()
    except imaplib.IMAP4.error as error:
        log.exception("Unable to logout of %s (%s)",
            account.name, error)
        sys.exit(1)
    else:
        log.debug("Successfully closed connection to %s",
            account.settings['server_name'])

log.info("Finished checking specified accounts and folders")
