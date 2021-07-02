# Add on Store Proposal

The intention of this proposal is to improve the end-to-end process and supporting infrastructure for hosting Addons.
This is the current plan from NV Access, it is a simplification of a [more complicated and highly automated plan](https://github.com/nvaccess/addon-store-submission/blob/c7d6f4fd9187fd0112de66b00caa62d774430d09/README.md). 
Inspiration has been taken from [Windows Package Manager Community repo](https://github.com/microsoft/winget-pkgs)
A highly automated process would be ideal, and we can keep the ideas in mind to work in that direction.

The main goal of this is to enable an "NVDA addon store" accessible from within NVDA itself.
In this proposal the word "store" is used to refer to the system used to store metadata about add-on releases and APIs to access this data.
Aims:
- Enable any necessary, API, process, or infrastructure to support users to browse, search, install and update Addons for NVDA.
- A secure and robust provision of addon-metadata.
- There is no intention of supporting paid addons at this stage.
- The process is intended to be as transparent as possible to make it simple (for developers) to understand the current state of the store or the state of a submission of a new / updated addon pending review.
The process should enable authors and reviewers to learn about and improve the addon-review process.

### About security 
Ensure that an add-on itself is safe to run, is a challenge that won't be addressed by this proposal.
Instead, this system can ensure that all updates to the metadata for add-on versions are reviewed, and allows clients of the system (website, NVDA) to verify that the addon package still matches what was reviewed.

### Past discussions
- About review process [conversation on the addons mailing list](https://nvda-addons.groups.io/g/nvda-addons/topic/69393202#10878) has been about reviewing Addons.
- While NV Access has some opinions on the review process, this proposal will first concern itself with the mechanics of the system rather than the considerations for a reviewer when looking at an addon.
For now, this step will just be referred to as 'review of addon performed'.
Later a "addon review check list" will be created.

### Non-exclusivity
This proposal does not intend to restrict Addon authors from developing, publishing, and distributing Addons outside of this store.
NVDA will still allow local installation from a `*.nvda-addon` file.

## Too Long; Didn't Read for Addon authors
With this proposal if an addon author wishes to submit their addon to be visible in this addon store they will need to:
- Add a file to this repo (via a pull request) containing metadata about published addons, including a download URL and hash of the addon package.
- To facilitate reviews, store their addon in an open (not private) repository.
- Get an "add-on reviewer" to review your addon and metadata submission, when this is approved it will be merged making it available.

## Too Long; Didn't Read for Addon reviewers
As an Addon reviewer you will:
- Look at pending PR's on the `addon-store-submission` repository.
- Follow the review process (yet to be documented).
- Either 'approve' the PR, or 'request changes' while providing feedback.

## Considerations

- Submissions and reviews should be easy to find and get the status of.
- Make it possible to automate many steps in the process, saving reviewers time.
- Once submitted an addon version should be immutable. No changing the addon on an external server, it must be updated in the store via the submission process.
- Allow addon authors to easily revoke a version if it is buggy / no longer supported. It should no longer be presented in the store, halting installation by new users.
- Enable support in the store for multiple versions of an Addon, based on NVDA version.
  - EG addon version 1.2.5 for NVDA 2019.3 and addon version 1.3.2 for NVDA 2020.1
- Enable support in the store for 'pre-release' Addons, for instance:
  - Addons being developed against alpha / beta NVDA.
  - Addons that want early feedback from end users.
  - End users can choose "show me pre-release addons"

## Overview

- Use GitHub reviews for store submissions.
- Use GitHub for storage of meta-data for addons available from the store.
- Use GitHub actions (or other integrations) to automate construction of the data store, and as many of the review checks as possible.
  This will all be open source and extensible by the community.

### Why GitHub reviews?
- GitHub is where much of the NVDA development ecosystem is already based.
- Handles all the of the CRUD ([create, read, update, delete](https://en.wikipedia.org/wiki/CRUD)) for users, authentication is handled, and we can determine how a user relates to an addon repository and what their permissions are for that repository. Are they actually an owner / maintainer?
- GitHub has a review system that allows for proposing changes and discussing these changes. We can leverage this for a store submission and review process.
- GitHub PR's provided an atomic view of a store submission.
- Interested parties can 'watch' PR's they care about without being subjected to the noise from PR's they don't care about.
- The result (open / merged / closed) of the PR is clear.
- GitHub allows us to manage permissions for accepting reviews more easily.

## Infrastructure

- `addon-store-submission` GitHub Repository
  - For Addon authors / reviewers.
  - Where new Addon versions are submitted
  - Where reviews of Addon submissions happen
  - For storage of meta-data about addons "in the store"
  - This repository acts as a back-end database, but is more transparent.
  - Since our needs are simple, preconfigured "views" of the data will suffice.
- NV Access server - To provide the endpoint for "available Addons" meta-data
  - While this is technically not necessary, it provides a good separation from implementation.
    If we wished to change our storage mechanism, we would not be breaking old versions of NVDA.

## `addon-store-submission` GitHub Repository

Essentially this repository holds metadata about all the accepted versions of Addons which are included in the store.
Metadata about old versions of an addon remains until it is explicitly removed or becomes invalid, allowing delivery to older versions of NVDA, or as a fall back in case the newer version is revoked after a critical bug is found.
Addons versions are submitted by submitting a pull request, adding a file for that version of the addon.

### Layout

Root directory of repository:
 - `readme.md` - A guide for submission
 - `addons/publisher1/addon1/majorVersion.minorVersion.patch.json`
 - `addons/publisher1/addon2/majorVersion.minorVersion.patch.json`
 - `addons/publisher2/addon3/majorVersion.minorVersion.patch.json`

Note: `publisher.addonName` will become the addon ID, and must be unique and match the addon ID from the addon manifest.

Example for the NV Access addon, 'NVDA - OCR': `addons/nvaccess/nvda-ocr/1.6.0.json`

### Metadata format
For a full description of the schema see:` _tools/addonVersion_schema.json`
- This includes an example of the file contents.

### Submitting an Addon version

#### Pre-requisites:
- Familiarity with GitHub
- Familiarity with Git, including working with branches.

Process to add a new NVDA-addon version:
1. Fork the `addon-store-submission` repository
1. On a new branch, copy the `_template_addon_release.json` file. 
   - Rename / move the file to `<publisher>/<addonName>/<version>.json`
   - `<publisher>` is the name of the add-on developer, E.G. "nvaccess"
   - `<addonName>` is the name of the add-on, E.G. "nv-speech-player"
   - `<version>` is the add-on version in the form: `Major.Minor.Patch` E.G. "2.4.1"
1. Create a PR on `addon-store-submission` repository
1. Automated checks for common issues will complete.
1. A review is performed (resulting in: request changes, approval)
   - Conducted by an NVDA add-on reviewer.
   - Manual review is done according to some published review check list (so that everyone knows what to expect)
1. The PR is merged, the add-on becomes available in the store.


### Checked during review
Many of these can be automated.
- Each modified file conforms to the schema
- Download URL is valid
- File from URL matches Sha256
- Version number matches add-on manifest.
- The file ID (`<publisher>.<addonName>`) matches the manifest 'name' field
- The version number from the file name is valid and matches the version in the manifest.

### Concerns
- With this ID scheme many add-ons will need to change their ID. Will this require previously saved user config to be moved to a new section of the config file?

### Other notes
- By using a git repository and and PR process, `git blame` and `git log` can be used to get more context about addons listed in the store. For instance:
  - When was the addon accepted
  - What did the review look like
  - How often does this addon have updates accepted
- GitHub allows assigning reviews to reviewers

## API data generation details

The NV Access server will be configured to respond to a Webhook to pull from this repository and run code to transform
the data.
This can regenerate the required views of the data for the exposed API's

### Overview

For each version of NVDA, the meta-data of the most recent (the highest version number) of each Addon is automatically
added, based on the data in 'addon-store-submission'.

Code for this will be stored in the `_tools` folder. This will enable interested parties to generate the same view of
the data locally.

### Data views

Required transformations of the data:
- `/NVDA API Version/addon-1-ID/release.json`
- `/NVDA API Version/addon-1-ID/pre-rel.json`
- `/NVDA API Version/addon-2-ID/release.json`
- `/NVDA API Version/all.json`

Notes:
- 'NVDA API Version' will be something like '2019.3', there will be one folder for each NVDA API Version.
- The `pre-rel.json` and `release.json` contain the information necessary for a store entry.
- The contents of `all.data` is all (pre-release and release) data for this NVDA API version together.
- The contents for each addon will include all the technical details required for NVDA to download, verify file integrity, and install.
- The file will include translations (if available) for the displayable metadata.

The simplicity of this is that the NV Access server can just forward these files on directly when asked
"what are the latest Addons for NVDA API Version X" or "What is the latest version of Addon-ID for NVDA API Version X".
Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated
away from GitHub for some reason.

## Suffix

### Terminology: Addon version vs Addon release

Since this proposal supports pre-release addons, I have tried to avoid using the term "addon release", instead favouring "addon version".
