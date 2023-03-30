
# Design Overview

## Background

Inspiration has been taken from [Windows Package Manager Community repo](https://github.com/microsoft/winget-pkgs)
A highly automated process would be ideal, and we can keep the ideas in mind to work in that direction.

Goal: enable an "NVDA add-on store" accessible from within NVDA itself.
"store" is used to refer to the system used to store metadata about add-on releases and APIs to access this data.
Aims:
- Enable any necessary, API, process, or infrastructure to support users to browse, search, install and update add-ons for NVDA.
- A secure and robust provision of addon-metadata.
- No intention of supporting paid add-ons at this stage.
- Transparent process, to make it simple (for developers) to understand the current state of the
  Add-on Store, or the state of a submission of a new / updated add-on.
- Faster release process for add-ons, by-passing human review.
- Non-subjective review process for add-ons.

## Considerations

- Submissions and automated checks should be easy to find and get the status of.
- Make it possible to automate many steps in the process.
- The `.nvda-addon` file accessible via the download URL must continue to match the SHA.
  NVDA will verify the file has not changed by comparing the checksum (SHA256).
  This gives users certainty when installing a "known version" of an add-on.
  To update or make changes to an add-on, a new unique URL should be used, and a new add-on
  submission made to the Add-on Store.
- Allow add-on authors to easily revoke a version if it is buggy / no longer supported.
  Removed releases are no longer presented in the store, halting new installations.
- Enable support in the store for multiple versions of an add-on, based on NVDA API version.
  - EG add-on version 1.2.5 for NVDA 2019.3 and add-on version 1.3.2 for NVDA 2020.1
- Enable support in the store for 'beta' and 'dev' add-ons, for instance:
  - 'dev' add-ons are being developed against alpha / beta / rc NVDA, these would only be offered to alpha / beta / rc NVDA users.
  - 'beta' add-ons are from authors who want early feedback from end users, signaling that not all edge cases are handled.
  - End users of NVDA can select "show pre-release add-ons"

## Overview

[Addon store system design diagram](./designOverview.svg) ([PlantUML markup](./designOverview.puml))

### Why GitHub Pull Requests?
- GitHub is where much of the NVDA development ecosystem is already based.
- Handles all the of the CRUD ([create, read, update, delete](https://en.wikipedia.org/wiki/CRUD))
  for users, authentication is handled, and we can determine how a user relates to an add-on
  repository and what their permissions are for that repository.
- GitHub PRs keep a record of the outcomes of automated checks.
  They also facilitate discussion should there be any confusion or disagreement with the outcome.
- GitHub PRs provided an atomic view of a store submission.
- The status (open / merged / closed) of the PR is clear.

## Infrastructure

- `addon-datastore` GitHub Repository
  - Authors submit new add-on versions.
  - The "source of truth" for add-on releases.
  - This repository acts as a back-end database, it is open and easy to inspect.
  - Since our needs are simple, preconfigured "views" of the data will suffice.
- `nvaccess/addon-datastore-validation` GitHub Repository
  - Metadata / submission schema.
  - Tools used to validate the submission.
- NV Access server - To provide the endpoint for "available add-ons" meta-data
  - While this is technically not necessary, it provides a good separation from implementation.
    If we wished to change our storage mechanism, we would not be breaking old versions of NVDA.


## API data generation details

Triggered by a new commit to the `master` branch, [a GitHub workflow](../../.github/workflows/transformDataToViews.yml), [addon-datastore-transform](https://github.com/nvaccess/addon-datastore-transform), transforms the data into the required views.

For each NVDA API version and channel, the add-on metadata with the highest version number is written.

These views are then committed by the GitHub Action to the [views branch](https://github.com/nvaccess/addon-datastore/tree/views).

### Data views
The following views will only be available on the [views branch](https://github.com/nvaccess/addon-datastore/tree/views) and located in a `views` folder.
Required transformations of the data:
- `/NVDA API Version/addon-1-ID/stable.json`
- `/NVDA API Version/addon-1-ID/beta.json`
- `/NVDA API Version/addon-2-ID/stable.json`

Notes:
- 'NVDA API Version' will be something like '2019.3', there will be one folder for each NVDA API Version.
- The `beta.json` and `stable.json` contain the information necessary for a store entry.
- The contents for each add-on will include all the technical details required for NVDA to download, verify file integrity, and install.
- The file will include translations (if available) for the displayable metadata.

This simplifies the processing on the hosting (E.G NV Access) server.

## `addon-datastore` GitHub Repository

Essentially this repository holds metadata about all the accepted versions of add-ons which are included in the store.
Metadata about old versions of an add-on remains until it is explicitly removed or becomes invalid.
This allows delivery to older versions of NVDA.
If a newer add-on release is removed (in response to a critical bug being found) NVDA can fall back
on a prior add-on release.
Add-ons versions are submitted via an issue form, which opens a pull request adding the JSON metadata file for that version of the add-on.

## NV Access Add-on Store endpoints

Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated away from GitHub for some reason.

### `GET`
Get a complete list of the latest add-on releases given an NVDA API version, channel and language.
Channel can be: all, dev, stable or beta.

- Format: `https://www.nvaccess.org/addonStore/<language>/<channel>/<NVDA API Version>.json`
- Example: <https://www.nvaccess.org/addonStore/en/all/2021.2.0.json>


### `GET` latest
Get a complete list of the latest add-on releases for any NVDA API version, given a channel and language.
Channel can be: all, dev, stable or beta.

- Format: `https://www.nvaccess.org/addonStore/<language>/<channel>/latest.json`
- Example: <https://www.nvaccess.org/addonStore/en/all/latest.json>

### Legacy
This endpoint mirrors the legacy [get.php, from the addonFiles repository](https://github.com/nvaccess/addonFiles/blob/master/get.php).

#### `addonslist` end-point

The `addonslist` parameter generates a list of list of add-ons using the same logic as the [latest end-point](#get-latest) for all channels.
The addonIds are generated to match the legacy naming schema.
For example, dev channel add-ons are named `addonId-dev` in the `addonslist`.

- Link: <https://www.nvaccess.org/addonStore/legacy?addonslist>

#### `file` end-point
The addonId supplied to the file parameter is fetched from the `addonslist`, returning the latest add-on version for that addonId.
`addonId` is case insensitive.

- Format: `https://www.nvaccess.org/addonStore/legacy?file=<addonId>`

### Other notes
- By using a git repository and PR process, `git blame` and `git log` can be used to get more
  context about add-ons listed in the store.
  For instance:
  - When was the add-on accepted?
  - What did the review look like?
  - How often is the add-on updated?
- GitHub allows assigning reviews to reviewers
