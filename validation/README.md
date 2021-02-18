# Validate NVDA add-on metadata ##

This is an "action repository" to validate metadata of add-ons sent to the NVDA's add-on store.

It performs the following checks:

- Ensures that metadata conforms to the ]addonVersion_schema.json file](https://github.com/nvdaes/validateNvdaAddonMetadata/blob/main/_validate/addonVersion_schema.json).
- Ensures that certain metadata match the appropriate values of the add-on manifest file.

## Usage ##

To validate metadata locally:

1. Clone this repo: `git clone https://github.com/nvdaes/validateNvdaAddonMetadata`
1. Install [jsonschema](https://pypi.org/project/jsonschema): `pip install jsonschema`
1. From the repo folder, _validate subfolder: `python validate.py <addonMetadataFile.json>`

To run unit tests:

1. Install [tox](https://pypi.org/project/tox): `pip install tox`
1. Run tox: `tox`
