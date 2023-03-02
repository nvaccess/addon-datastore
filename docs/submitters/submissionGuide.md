# Submission Guide

If an add-on author wishes to submit their add-on to be visible in this add-on store they will need to:
- Copy and fill out the metadata template
- Create a pull request to merge the branch to master of this repository.

## Pre-requisites:
- Familiarity with GitHub
- Familiarity with Git, including working with branches.

## Set up
Fork the `addon-datastore` repository

## Create an add-on version file for submission
You can create this manually, or generate this from an add-on manifest file.

### Manual file creation
On a new branch, copy the `_template_addon_release.json` file. 
- Rename and move the file to `addons/<addonID>/<version>.json`
- `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, e.g. "speechPlayer"
- `<version>` is the add-on version in the form: `Major.Minor.Patch` e.g. "2.4.1"

### Generating from an add-on manifest
1. Install requirements to python environment:
`pip install requests configobj`
1. Convert an add-on to a json file:
`python convertAddonManifest.py [addonId] [stable|beta|dev] [addonUrl]`
	- `addonID` is the ID of the add-on. This should match the `name` field in the add-on manifest, e.g. "speechPlayer"
	- `stable|beta|dev` are the channel options, choose one of these.
	- `addonUrl` is where the addon file is hosted.
1. Edit the auto-generated json file as required.

## Filling out the template

### addonId
The ID for the addon.
This should match the name field in the addon manifest and the folder name for the submission.
The convention is a camelCaseName.

Example: `easyAddonTech`

### channel
Should be `"stable", "beta" or "dev"`.

**Stable:** Offered to users of any compatible version of NVDA.

**Beta**: Allows add-on authors to target a stable NVDA release and get feedback from early adopter users before publishing add-on as stable.
Offered to users of any compatible version of NVDA.

**Dev**: Not offered to users of stable NVDA, only pre-release NVDA.
This includes alpha, beta, rc, try, or dev builds.
This channel can be used for developing add-ons against the newest unreleased additions to NVDA, or to stay up to date with compatibility breaking changes in an API breaking release cycle.

### addonVersionNumber
The version of the add-on, as a major-minor-patch dictionary.
Add-on versions are expected to be unique for the addonId,
meaning that a beta, stable and dev add-on version cannot share a version number.
This is so there can be a unique ordering of newest to oldest.

The suggested convention is to increment the patch version number for dev versions,
increment the minor version number for beta versions,
and increment the major version number for stable versions.

Example:
```json
{
	"major": 21,
	"minor": 6,
	"patch": 0
}
```

### addonVersionName
The addon version being released.
Must match the version in the addon manifest and the file name for the submission.

Example: `21.6.0`.

### displayName
The name that will be displayed in English for the addon.

Example: `"Easy Addon"`

### publisher
The name of the individual, group, or company responsible for the addon.

Example: `"NV Access"`

### description
The English description of the addon that will be displayed for the addon.
	
Example: `"Makes doing XYZ easier"`

### homepage
Optional.
If the addon has a homepage where users can get more information about the addon, you can specify it here.

Example: `"https://github.com/nvaccess/addon-datastore"`

### minNVDAVersion
The addon will not work with versions of NVDA prior to this version.

Example:
```json
{
	"major": 2021,
	"minor": 1,
	"patch": 0
}
```

### lastTestedVersion
The add-on has been tested up to and including this version of NVDA.

Example:
```json
{
	"major": 2020,
	"minor": 4,
	"patch": 0
}
```

### URL
To allow directly downloading the *.nvda-addon file.
The URL should remain valid indefinitely.
GitHub release URL's are recommended.

Example: `"https://github.com/nvaccess/addon-datastore/releases/download/v0.1.0/myAddon.nvda-addon"`

### sha256
The SHA256 checksum for the *.nvda-addon file.
To calculate a SHA256 sum on Windows, run the following from command prompt:

```cmd
certutil -hashfile <pathToAddonFile.nvda-addon> SHA256
```

Example: `"69D84CA8899800A5575CE31798293CD4FEBAB1D734A07C2E51E56A28E0DF8C82"`

### sourceURL
Allows reviewers to inspect the source code for common issues.

Example: `"https://github.com/nvaccess/addon-datastore/"`

### license
The short name of the license

Example: `"GPL v2"`

### licenseURL
Optional.
A URL to the full license for the addon.

Example: `"https://github.com/nvaccess/addon-datastore/license.MD"`

### Metadata format
For a full description of the schema see the
[_validate/addonVersion_schema.json file](https://github.com/nvaccess/addon-datastore-validation/blob/main/_validate/addonVersion_schema.json).
It includes an example of the file contents.

## Submitting your add-on version file
1. Create a PR to merge your branch into master on the `addon-datastore` repository
1. Automated checks to validate the submission will complete.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
GitHub requires manual approval for the automated checks to run on an author's the first submission to the repository.
1. If the checks pass, the PR should be merged automatically.
However, a human review process may be required.
1. When the PR is merged the add-on becomes available in the store.
