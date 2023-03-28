# Submission Guide
If your add-on was hosted on [addonFiles](https://github.com/nvaccess/addonFiles) please read the [migrating to datastore guide](./migratingFromAddonFiles.md).

## Pre-requisites:
Familiarity with GitHub

## Create an add-on version file for submission
Each submission to the addon-datastore is structured as a JSON file, containing all the metadata needed for the NVDA add-on store.
You can create this manually, or generate this by submitting an issue.
Descriptions for the fields of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).

### Submit from an issue form
1. Select ["Add-on registration" from the new issue options](https://github.com/nvaccess/addon-datastore/issues/new/choose).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission.
The issue form and the add-on's manifest are used to create a JSON file.
This JSON file is submitted as a pull request to the repository.
1. Automated checks are ran to validate the submission.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks fail, a comment should be added to the pull request outlining the failure.
To address the issues, resubmit the issue form.
You may need to also update your add-on manifest.
Descriptions for the fields of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. If the checks pass, the PR should be merged automatically.
The add-on should soon become available in the store.

### Manual file creation
1. Fork the `addon-datastore` repository
1. On a new branch, copy the `_template_addon_release.json` file. 
	- Rename and move the file to `addons/<addonID>/<version>.json`
	- `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, e.g. "speechPlayer"
	- `<version>` is the add-on version in the form: `Major.Minor.Patch` e.g. "2.4.1"
1. Fill out the template.
Descriptions for the fields of JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. Create a PR to merge your branch into master on the `addon-datastore` repository.
1. Automated checks are ran to validate the submission.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks fail, the PR will not be automatically merged.
You can check [the GitHub actions log](https://github.com/nvaccess/addon-datastore/actions/workflows/checkPullRequest.yml?query=event%3Apull_request+is%3Afailure) to find more information on the failure.
To address the issues, resubmit the issue form.
You may need to also update your add-on manifest.
1. If the checks pass, the PR should be merged automatically.
The add-on should soon become available in the store.

## Registering an add-on in the translation system
Optional.
Some authors may wish to include their add-on in the translations system.
To do this, follow the steps to register the add-on in [mrconfig](https://github.com/nvaccess/mrconfig/blob/master/readme.md#steps-for-addon-authors).
