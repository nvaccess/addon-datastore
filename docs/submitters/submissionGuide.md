# Submission Guide
If your add-on was hosted on [addonFiles](https://github.com/nvaccess/addonFiles) please read the [migrating to datastore guide](./migratingFromAddonFiles.md).

Submitted add-ons should comply with the [NVDA code of conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md)

## Background
Submitting an add-on version is done via a GitHub issue form.
A JSON metadata file is generated from the issue form and the add-on's manifest.
A detailed description of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
When the issue form is submitted, the JSON file is generated and submitted as a pull request to the repository.

Automated validation checks are run against the pull request.
If there are validation errors, they will be commented on the pull request.
Otherwise, the pull request will be merged, the issue will be closed and the add-on will become available in the Add-on Store.

It is expected that submitters do not hijack add-on IDs by submitting an add-on which shares an add-on ID of an existing add-on.
If you are an add-on author and your add-on ID has been hijacked, please open an issue or contact <info@nvaccess.org>.
Submitters which abuse this process will have their submission approval revoked.

## Steps to submit an add-on
1. Select ["Add-on registration" from the new issue options](https://github.com/nvaccess/addon-datastore/issues/new/choose).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission, and generate a pull request to submit your add-on to the store.
1. If this is your first submission, manual approval will be required to be added to the approved submitters list.
1. Automated checks are ran on the pull request to validate the submission.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks fail, a comment should be added to the issue outlining the failure.
To address the issues, resubmit the issue form.
You may need to also update your add-on manifest.
Descriptions for the fields of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. If the checks pass, the pull request should be merged automatically.
The add-on should soon become available in the store.

## Registering an add-on in the translation system
Optional.
Some authors may wish to include their add-on in the translations system.
To do this, follow the steps to register the add-on in [mrconfig](https://github.com/nvaccess/mrconfig/blob/master/readme.md#steps-for-addon-authors).
