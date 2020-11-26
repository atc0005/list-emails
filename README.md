# ls-emails

Small Python 3 script intended to help ease the burden of processing multiple
email accounts.

This script can be used to mass-list the contents of specific
email accounts and folders as part of preparing a report regarding actions
taken on those items.

## Status

**This project is retired.**

The functionality provided by the `list_emails.py` script has been superseded
by the new `list-emails` application provided by `v0.3.0` of the
atc0005/check-mail project. See the [README for the check-mail
project](https://github.com/atc0005/check-mail/blob/master/README.md) and/or
the [Pull Request](https://github.com/atc0005/check-mail/pull/125) which added
the `list-emails` application to that project.

## Requirements

- Tested: Python 3.6.5
- Probably: Python 3.4.x+

Windows, Linux or Mac OS *should* work equally well, though as I write this I
have only tested on Windows 10 Version 1803.

## Repo layout

File/Path | Purpose | Notes
--------- | ------- | -----
`doc` | Notes, other material intended to help explain use of project code | Pretty bare
`templates` | Contains templates used directly by the script and those intended for use by user | `templates/accounts.ini.tmpl` resides here
`templates/accounts.ini.tmpl` | Copy, paste and modify as `accounts.ini` | Only needed once
`log` | Temporary log files created by the script as it runs | The script does not make any effort to prune old files, that falls on the user to handle
`output` | Directory where text files are created by the script containing email subject lines | See `accounts.ini`
`accounts.ini` | List of email account configuration options. | Should be manually created from `templates/accounts.ini.tmpl` file, included within svn:ignore list
`list_emails.py` | Main script | Run from command-line from the same directory in which the script resides. Referenced internally as `ls-emails`, though the filename is currently `list_emails.py`
`LICENSE` | License for this collection of content | Intended to allow freedom of use and clear responsibility regarding providing enhancements back to the main project
`README.md` | Main doc file for this project | Please submit a PR or bug report for any missing or incorrect coverage

## Directions

### Normal operation

1. Install stock/official Python as noted previously.
1. Clone/checkout this project code to a location on your system that you have
   read/write access to (e.g., a "standard user" location).
1. Copy `templates/accounts.ini.tmpl` to the same folder that the script
   resides in. Rename the file `accounts.ini`.
1. Fill in the configuration file using username/password info for each
   account that you wish to retrieve Subject lines for. Update any placeholder
   values with real production values that match your environment.
1. Make sure to review the configuration file and add double-quotes around
   each folder name if they are not already there. The latest version of the
   template file *should* illustrate the required syntax.
1. Open a command prompt.
1. Change to the directory where the script is located.
1. Type `list_emails.py`.
1. Press the Enter key.
1. Review the files within the `output` directory.

### Troubleshooting

1. If the results are inconclusive or odd behavior is encountered, review
   the log files within the `log` directory.
1. If the problem is still not clear:
    1. sanitize the contents of the log file
    1. open a new issue with as clear an error report as you can provide
    1. attach the sanitized log file

## References

- <https://github.com/atc0005/check-mail>
- <https://github.com/atc0005/list-emails>
- see [doc/references.md](doc/references.md)
