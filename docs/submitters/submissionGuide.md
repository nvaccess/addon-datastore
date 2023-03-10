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
Detailed descriptions for the fields of JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).

## After submitting your issue
1. Automated checks to validate the submission will complete.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks pass, the PR should be merged automatically.
A comment will be posted on the pull request explaining the validation errors.
1. When the PR is merged the add-on becomes available in the store.
