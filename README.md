# Add on Store

The intention the add-on store is to improve the end-to-end process and supporting infrastructure for hosting Addons.
This is the current plan from NV Access, work is ongoing.
Inspiration has been taken from [Windows Package Manager Community repo](https://github.com/microsoft/winget-pkgs)
A highly automated process would be ideal, and we can keep the ideas in mind to work in that direction.

Goal: enable an "NVDA addon store" accessible from within NVDA itself.
In this proposal the word "store" is used to refer to the system used to store metadata about add-on releases and APIs to access this data.
Aims:
- Enable any necessary, API, process, or infrastructure to support users to browse, search, install and update Addons for NVDA.
- A secure and robust provision of addon-metadata.
- No intention of supporting paid addons at this stage.
- Transparent process, to make it simple (for developers) to understand the current state of the
  Add-on Store, or the state of a submission of a new / updated addon.
- Faster release process for add-ons, by-passing human review.
- Non-subjective review process for add-ons.

### About security 
Ensuring that an add-on is safe to run is a difficult challenge that isn't addressed here.
However, the metadata for a new submission (add-on release) can be confirmed to match its manifest
description.
Additionally, add-on file integrity can be enforced via a Sha256 checksum.
The checksum allows NVDA to ensure that addon releases are immutable.

### Human review process / code audit
- NV Access doesn't require a manual review of the add-on (code or user experience) itself
  before the add-on submission.
- Source code reviews or audits could exist outside the store.
  The Sha256 checksum of the `nvda-addon` prevents undetected changes.
- User reviews/rating of add-ons are currently out of scope.

### Non-exclusivity
This proposal does not intend to restrict add-on authors from developing, publishing, and distributing an add-on outside this store.
NVDA will still allow local installation from a `*.nvda-addon` file.

## Too Long; Didn't Read for Addon authors
With this proposal if an addon author wishes to submit their addon to be visible in this addon store they will need to:
- Copy and file out the metadata template
- Create a pull request to merge the branch to master of this repository.

## Too Long; Didn't Read for Addon reviewers
Reviews of metadata will be automated.
You are welcome to review code / UX of addons and provide that feedback directly to addon authors.

## Considerations

- Submissions and automated checks should be easy to find and get the status of.
- Make it possible to automate many steps in the process.
- The `.nvda-addon` file accessible via the download URL must continue to match the SHA.
  NVDA will verify the file has not changed by comparing the checksum (SHA256).
  This gives users certainty when installing a "known version" of an addon.
  To update or make changes to an add-on, a new unique URL should be used, and a new add-on
  submission made to the Add-on Store.
- Allow addon authors to easily revoke a version if it is buggy / no longer supported.
  Removed releases are no longer presented in the store, halting new installations.
- Enable support in the store for multiple versions of an Addon, based on NVDA API version.
  - EG addon version 1.2.5 for NVDA 2019.3 and addon version 1.3.2 for NVDA 2020.1
- Enable support in the store for 'beta' Addons, for instance:
  - Addons being developed against alpha / beta NVDA.
  - Addons that want early feedback from end users.
  - End users can choose "show me beta addons"

## Overview

- Use GitHub pull requests for store submissions.
- Use GitHub for storage of meta-data for addons available from the store.
- Use GitHub actions (or other integrations) to automate construction of the data store, and as many of the metadata checks as possible.
  This will all be open source and extensible by the community.

### Why GitHub Pull Requests?
- GitHub is where much of the NVDA development ecosystem is already based.
- Handles all the of the CRUD ([create, read, update, delete](https://en.wikipedia.org/wiki/CRUD))
  for users, authentication is handled, and we can determine how a user relates to an addon
  repository and what their permissions are for that repository.
- GitHub PR's keep a record of the outcomes of automated checks.
  They also facilitate discussion should there be any confusion or disagreement with the outcome.
- GitHub PR's provided an atomic view of a store submission.
- The status (open / merged / closed) of the PR is clear.

## Infrastructure

- `addon-store-submission` GitHub Repository
  - Authors submit new add-on versions.
  - The "source of truth" for add-on releases.
  - This repository acts as a back-end database, it is open and easy to inspect.
  - Since our needs are simple, preconfigured "views" of the data will suffice.
- `nvaccess/validateNvdaAddonMetadata` GitHub Repository
  - Metadata / submission schema.
  - Tools used to validate the submission.
- NV Access server - To provide the endpoint for "available Addons" meta-data
  - While this is technically not necessary, it provides a good separation from implementation.
    If we wished to change our storage mechanism, we would not be breaking old versions of NVDA.

## `addon-store-submission` GitHub Repository

Essentially this repository holds metadata about all the accepted versions of Addons which are included in the store.
Metadata about old versions of an addon remains until it is explicitly removed or becomes invalid.
This allows delivery to older versions of NVDA.
If a newer add-on release is removed (in response to a critical bug being found) NVDA can fall back
on a prior add-on release.
Addons versions are submitted by submitting a pull request, adding a file for that version of the addon.

### Layout

Root directory of repository:
 - `readme.md` - A guide for submission
 - `addons/addon1/majorVersion.minorVersion.patch.json`
 - `addons/addon2/majorVersion.minorVersion.patch.json`
 - `addons/addon3/majorVersion.minorVersion.patch.json`

Note: `addonName` is the add-on ID, and must be unique and match the add-on ID from the addon manifest.

Example for the NV Access addon, 'NVDA - OCR':
- Filename: `addons/nvda-ocr/1.6.0.json`
- add-on ID `nvda-ocr`

### Metadata format
For a full description of the schema see the
[_validate/addonVersion_schema.json file](https://github.com/nvaccess/validateNvdaAddonMetadata/blob/main/_validate/addonVersion_schema.json).
It includes an example of the file contents.

### Submitting an Addon version

#### Pre-requisites:
- Familiarity with GitHub
- Familiarity with Git, including working with branches.

Process to add a new NVDA-addon version:
1. Fork the `addon-store-submission` repository
1. On a new branch, copy the `_template_addon_release.json` file. 
   - Rename / move the file to `addons/<addonID>/<version>.json`
   - `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, E.G. "nv-speech-player"
   - `<version>` is the add-on version in the form: `Major.Minor.Patch` E.G. "2.4.1"
1. Fill out the template.
1. Create a PR to merge your branch into master on the `addon-store-submission` repository
1. Automated checks for common issues will complete. Either giving feedback or merging the PR.
3. When the PR is merged the add-on becomes available in the store.


### Automated checks
See https://github.com/nvaccess/validateNvdaAddonMetadata

### Other notes
- By using a git repository and PR process, `git blame` and `git log` can be used to get more
  context about addons listed in the store.
  For instance:
  - When was the addon accepted?
  - What did the review look like?
  - How often is the add-on updated?
- GitHub allows assigning reviews to reviewers

## API data generation details

Triggered by a new commit, a GitHub workflow transforms the data into the required views.
These views of the data will be committed by the GitHub Action to a `views` branch.

### Overview

For each version of NVDA, the meta-data of the most recent (the highest version number) of each Addon is automatically
added, based on the data in 'addon-store-submission'.

Code for this will be stored in the `_tools` folder.
This will enable interested parties to generate the same view of the data locally.
This code will have automated tests.

### Data views
The following views will only be available on a `views` branch, and located in a `views` folder.
Required transformations of the data:
- `/NVDA API Version/addon-1-ID/release.json`
- `/NVDA API Version/addon-1-ID/beta.json`
- `/NVDA API Version/addon-2-ID/release.json`

Notes:
- 'NVDA API Version' will be something like '2019.3', there will be one folder for each NVDA API Version.
- The `beta.json` and `release.json` contain the information necessary for a store entry.
- The contents for each addon will include all the technical details required for NVDA to download, verify file integrity, and install.
- The file will include translations (if available) for the displayable metadata.

The simplicity of this is that the NV Access server can just forward these files on directly when asked
"what are the latest Addons for NVDA API Version X" or "What is the latest version of Addon-ID for NVDA API Version X".
Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated
away from GitHub for some reason.

## Suffix

### Terminology: Addon version vs Addon release

Since this proposal supports beta addons, I have tried to avoid using the term "addon release", instead favouring "addon version".
