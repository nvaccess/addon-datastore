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
You can create this manually, or generate this by submitting an issue.

### Submit from an issue form
Select ["Add-on registration" from the new issue options](https://github.com/nvaccess/addon-datastore/issues/new/choose).
Fill out and submit the issue form.

A PR should automatically open.
If the PR fails to auto-merge, re-submit the auto-generated JSON file by following the "Manual file creation" steps.

### Manual file creation
1. On a new branch, copy the `_template_addon_release.json` file. 
	- Rename and move the file to `addons/<addonID>/<version>.json`
	- `<addonID>` is the ID of the add-on. This should match the `name` field in the add-on manifest, e.g. "speechPlayer"
	- `<version>` is the add-on version in the form: `Major.Minor.Patch` e.g. "2.4.1"
1. Fill out the template.
Descriptions for the fields of JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. Create a PR to merge your branch into master on the `addon-datastore` repository.

## After submitting your add-on version file
1. Automated checks to validate the submission will complete.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
GitHub requires manual approval for the automated checks to run on an author's first submission to the repository.
1. If the checks pass, the PR should be merged automatically.
However, a human review process may be required.
1. When the PR is merged the add-on becomes available in the store.
