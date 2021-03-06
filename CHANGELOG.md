# Changelog

## Overview

All notable changes to this project will be documented in this file.

The format is based on [Keep a
Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Please [open an issue](https://github.com/atc0005/list-emails/issues) for any
deviations that you spot; I'm still learning!.

## Types of changes

The following types of changes will be recorded in this file:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [Unreleased]

- placeholder

## [v0.1.4] - 2020-09-14

### Changed

- Use From header to generate missing Subject line
  - instead of skipping emails with missing Subject lines

### Fixed

- imaplib.IMAP4.error: command CLOSE illegal in state AUTH, only allowed in
  states SELECTED

## [v0.1.3] - 2020-09-14

### Added

- Add `CHANGELOG.md` file

### Changed

- Explicitly set stdout and stderr output encoding

### Fixed

- AttributeError: 'NoneType' object has no attribute 'replace'

## [v0.1.2] - 2018-11-29

### Fixed

- Fix UnicodeEncodeError charmap codec errors

## [v0.1.1] - 2018-08-20

### Fixed

- Add missing content to template config file

## [v0.1.0] - 2018-08-20

### Added

Initial release; add first draft of list-emails script.

[Unreleased]: https://github.com/atc0005/list-emails/compare/v0.1.4...HEAD
[v0.1.4]: https://github.com/atc0005/list-emails/releases/tag/v0.1.4
[v0.1.3]: https://github.com/atc0005/list-emails/releases/tag/v0.1.3
[v0.1.2]: https://github.com/atc0005/list-emails/releases/tag/v0.1.2
[v0.1.1]: https://github.com/atc0005/list-emails/releases/tag/v0.1.1
[v0.1.0]: https://github.com/atc0005/list-emails/releases/tag/v0.1.0
