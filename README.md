# Add on Store

The intention the add-on store is to improve the end-to-end process and supporting infrastructure for hosting add-ons.
This is the current plan from NV Access, work is ongoing.
Inspiration has been taken from [Windows Package Manager Community repo](https://github.com/microsoft/winget-pkgs)
A highly automated process would be ideal, and we can keep the ideas in mind to work in that direction.

Goal: enable an "NVDA add-on store" accessible from within NVDA itself.
In this proposal the word "store" is used to refer to the system used to store metadata about add-on releases and APIs to access this data.
Aims:
- Enable any necessary, API, process, or infrastructure to support users to browse, search, install and update add-ons for NVDA.
- A secure and robust provision of addon-metadata.
- No intention of supporting paid add-ons at this stage.
- Transparent process, to make it simple (for developers) to understand the current state of the
  Add-on Store, or the state of a submission of a new / updated add-on.
- Faster release process for add-ons, by-passing human review.
- Non-subjective review process for add-ons.

### About security 
Ensuring that an add-on is safe to run is a difficult challenge that isn't addressed here.
However, the metadata for a new submission (add-on release) can be confirmed to match its manifest
description.
Additionally, add-on file integrity can be enforced via a Sha256 checksum.
The checksum allows NVDA to ensure that add-on releases are immutable.

### Human review process / code audit
- NV Access doesn't require a manual review of the add-on (code or user experience) itself
  before the add-on submission.
- Source code reviews or audits could exist outside the store.
  The Sha256 checksum of the `nvda-addon` prevents undetected changes.
- User reviews/rating of add-ons are currently out of scope.

### Non-exclusivity
This proposal does not intend to restrict add-on authors from developing, publishing, and distributing an add-on outside this store.
NVDA will still allow local installation from a `*.nvda-addon` file.
The data hosted here is distributed under the [ODC-PDDL](https://opendatacommons.org/licenses/pddl/1-0/) license.
A plain language summary can be found [here](https://opendatacommons.org/licenses/pddl/summary/).

## Too Long; Didn't Read for add-on authors
With this proposal if an add-on author wishes to submit their add-on to be visible in this add-on store they will need to:
- Copy and file out the metadata template
- Create a pull request to merge the branch to master of this repository.

## Too Long; Didn't Read for add-on reviewers
Reviews of metadata will be automated.
You are welcome to review code / UX of add-ons and provide that feedback directly to add-on authors.

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
- Enable support in the store for 'beta' add-ons, for instance:
  - add-ons being developed against alpha / beta NVDA.
  - add-ons that want early feedback from end users.
  - End users can choose "show me beta add-ons"

## Overview

[Addon store system design diagram](./docs/design/designOverview.svg) ([PlantUML markup](./docs/design/designOverview.puml))

- Use GitHub pull requests for store submissions.
- Use GitHub for storage of meta-data for add-ons available from the store.
- Use GitHub actions (or other integrations) to automate construction of the data store, and as many of the metadata checks as possible.
  This will all be open source and extensible by the community.

### Why GitHub Pull Requests?
- GitHub is where much of the NVDA development ecosystem is already based.
- Handles all the of the CRUD ([create, read, update, delete](https://en.wikipedia.org/wiki/CRUD))
  for users, authentication is handled, and we can determine how a user relates to an add-on
  repository and what their permissions are for that repository.
- GitHub PR's keep a record of the outcomes of automated checks.
  They also facilitate discussion should there be any confusion or disagreement with the outcome.
- GitHub PR's provided an atomic view of a store submission.
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

## `addon-datastore` GitHub Repository

Essentially this repository holds metadata about all the accepted versions of add-ons which are included in the store.
Metadata about old versions of an add-on remains until it is explicitly removed or becomes invalid.
This allows delivery to older versions of NVDA.
If a newer add-on release is removed (in response to a critical bug being found) NVDA can fall back
on a prior add-on release.
Add-ons versions are submitted by submitting a pull request, adding a file for that version of the add-on.

### Layout

Root directory of repository:
 - `readme.md` - A guide for submission
 - `addons/addon1/majorVersion.minorVersion.patch.json`
 - `addons/addon2/majorVersion.minorVersion.patch.json`
 - `addons/addon3/majorVersion.minorVersion.patch.json`

Note: `addonName` is the add-on ID, and must be unique and match the add-on ID from the add-on manifest.

Example for the NV Access add-on, 'NVDA - OCR':
- Filename: `addons/nvda-ocr/1.6.0.json`
- add-on ID `nvda-ocr`

### Metadata format
For a full description of the schema see the
[_validate/addonVersion_schema.json file](https://github.com/nvaccess/addon-datastore-validation/blob/main/_validate/addonVersion_schema.json).
It includes an example of the file contents.

### Submitting an add-on version

#### Pre-requisites:
- Familiarity with GitHub
- Familiarity with Git, including working with branches.

Process to add a new NVDA add-on version:
1. Fork the `addon-datastore` repository
1. On a new branch, copy the `_template_addon_release.json` file. 
   - Rename / move the file to `addons/<addonID>/<version>.json`
   - `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, E.G. "nv-speech-player"
   - `<version>` is the add-on version in the form: `Major.Minor.Patch` E.G. "2.4.1"
1. Fill out the template.
1. Create a PR to merge your branch into master on the `addon-datastore` repository
1. Automated checks for common issues will complete. Either giving feedback or merging the PR.
3. When the PR is merged the add-on becomes available in the store.


### Automated checks
See https://github.com/nvaccess/addon-datastore-validation

### Other notes
- By using a git repository and PR process, `git blame` and `git log` can be used to get more
  context about add-ons listed in the store.
  For instance:
  - When was the add-on accepted?
  - What did the review look like?
  - How often is the add-on updated?
- GitHub allows assigning reviews to reviewers

## API data generation details

Triggered by a new commit to the `master` branch, [a GitHub workflow](./.github/workflows/transformDataToViews.yml), [addon-datastore-transform](https://github.com/nvaccess/addon-datastore-transform), transforms the data into the required views.

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

## NV Access Add-on Store endpoints

Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated away from GitHub for some reason.

### `GET` All
Get a complete list of the latest add-on releases.
Includes both stable and beta versions

- Format: `https://www.nvaccess.org/addonStore/<language>/all/<NVDA API Version>.json`
- Example: <https://www.nvaccess.org/addonStore/en/all/2021.2.0.json>

### `GET` All stable
Get a complete list of the latest stable add-on releases.
Includes only stable versions

- Format: `https://www.nvaccess.org/addonStore/<language>/stable/<NVDA API Version>.json`
- Example: <https://www.nvaccess.org/addonStore/en/stable/2021.2.0.json>

### `GET` All beta
Get a complete list of the latest beta add-on releases.
Includes only beta versions

- Format: `https://www.nvaccess.org/addonStore/<language>/beta/<NVDA API Version>.json`
- Example: <https://www.nvaccess.org/addonStore/en/beta/2021.2.0.json>

## Suffix

### Terminology: add-on version vs add-on release

Since this proposal supports beta addons, I have tried to avoid using the term "add-on release", instead favouring "add-on version".
