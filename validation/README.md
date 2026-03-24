# Validate NVDA add-on metadata

The code aims to validate the metadata of add-ons submitted to
[NVDA's add-on store](https://github.com/nvaccess/addon-datastore).

* Check that the added metadata:
  * Conforms with the
  [addonVersion_schema.json file](./_validate/addonVersion_schema.json).
  * File has the correct path and name: `addon1/majorVersion.minorVersion.patch.json`
  * Download URL is valid:
    * Must start with "https://" and end with".nvda-addon"
    * The `*.nvda-addon` file can be downloaded
  * The Sha256 of the downloaded `*.nvda-addon` file matches.
* Check data matches the addon's manifest file.
  * The manifest exists in the downloaded `*.nvda-addon` file and can be loaded by the `AddonManifest` class.
  * The submission addonName matches the manifest summary field
  * The submission description matches the manifest description field
  * The homepage URL matches the manifest URL field
  * The addon versions match
  * The last tested & minimum required versions are valid NVDA API versions.

If all is valid, "Congratulations: manifest, metadata and file path are valid" is printed.

## Local Usage

To try validating an addon submission on your own machine.

From cmd.exe:

1. From the repo folder, run: `runvalidate <pathToAddonMetadataFile.json> <pathToFileWithAPIVersions.json>`

