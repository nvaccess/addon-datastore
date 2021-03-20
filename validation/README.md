# Validate NVDA add-on metadata ##

This is an "action repository" to validate metadata of add-ons sent to the NVDA's add-on store.

It performs the following checks:

- Ensures that metadata conforms to the ]addonVersion_schema.json file](https://github.com/nvdaes/validateNvdaAddonMetadata/blob/main/_validate/addonVersion_schema.json).
- Ensures that certain metadata match the appropriate values of the add-on manifest file.

## Dependencies ##

* [Python](https://www.python.org/). This has been tested with versions 3.8 and 3.9, 32 bit, but other versions may work too.

## Usage ##

To validate metadata locally:

From the command line (cmd):

1. Clone this repo: `git clone https://github.com/nvdaes/validateNvdaAddonMetadata`
1. From the repo folder, run: `runvalidate <pathToAddonMetadataFile.json>`

To run unit tests:

1. Install [tox](https://pypi.org/project/tox): `pip install tox`
1. Run tox: `tox`

To lint source code (Python files):

1. From the repo folder, run: `runlint`
