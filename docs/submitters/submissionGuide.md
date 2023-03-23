# Submission Guide

If an add-on author wishes to submit their add-on to be visible in this add-on store they will need to:
- Copy and fill out the metadata template
- Create a pull request to merge the branch to master of this repository.

## Pre-requisites:
- Familiarity with GitHub
- Familiarity with Git, including working with branches.

## Create an add-on version file for submission
You can create this manually, or generate this by submitting an issue.

### Submit from an issue form
1. Select ["Add-on registration" from the new issue options](https://github.com/nvaccess/addon-datastore/issues/new/choose).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission.
The form and your add-on's manifest are used to create a JSON file.
This JSON file is submitted as a pull request to the repository.

### Manual file creation
1. Fork the `addon-datastore` repository
1. On a new branch, copy the `_template_addon_release.json` file. 
	- Rename and move the file to `addons/<addonID>/<version>.json`
	- `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, e.g. "speechPlayer"
	- `<version>` is the add-on version in the form: `Major.Minor.Patch` e.g. "2.4.1"
1. Fill out the template.
Descriptions for the fields of JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. Create a PR to merge your branch into master on the `addon-datastore` repository.

## After submitting your add-on version file
1. Automated checks are ran to validate the submission.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks pass, the PR should be merged automatically.
1. If the checks fail, a comment should be added to the pull request outlining the failure.
To address the issues, resubmit the issue form or manual pull request.
You may need to also update your add-on manifest.
Descriptions for the fields of JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. When the PR is merged the add-on becomes available in the store.
