## JSON Metadata Schema details
For a full description of the schema see the
[_validate/addonVersion_schema.json file](https://github.com/nvaccess/addon-datastore-validation/blob/main/_validate/addonVersion_schema.json).
It includes an example of the file contents.

### addonId
The ID for the addon.
This should match the name field in the addon manifest and the folder name for the submission.
The suggested convention is a camelCaseName.

Example: `easyAddonTech`

### channel
Should be `"stable", "beta" or "dev"`.

**Stable:** Suggested for add-on versions which are stable, and have been tested with a stable version of NVDA.

**Beta**: Suggested for getting add-on feedback from early adopter users before publishing an add-on as stable.
Suggested for testing with stable, beta or rc NVDA releases.

**Dev**: This channel is suggested to be used with any preview or pre-release version of NVDA.
This is useful for testing compatibility breaking changes in an API breaking release cycle, and unreleased additions to the NVDA API.

### addonVersionNumber
The version of the add-on, as a major-minor-patch dictionary.
Add-on versions are expected to be unique for the addonId,
meaning that a beta, stable and dev add-on version cannot share a version number.
This is so there can be a unique ordering of newest to oldest.
Add-on versions should be released in order, newer versions will encourage an update.
Users may be able to upgrade across channels in future.

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
Must match the summary in the addon manifest.

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
Must match the url in the addon manifest and the file name for the submission.

Example: `"https://github.com/nvaccess/addon-datastore"`

### minNVDAVersion
The add-on will not work with versions of NVDA prior to this version.
Must be a valid NVDA API version.
Valid NVDA API versions are listed in [nvdaAPIVersions.json](https://github.com/nvaccess/addon-datastore-transform/blob/main/nvdaAPIVersions.json).

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
Must be a valid NVDA API version.
Valid NVDA API versions are listed in [nvdaAPIVersions.json](https://github.com/nvaccess/addon-datastore-transform/blob/main/nvdaAPIVersions.json).

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
GitHub release URLs are recommended.

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