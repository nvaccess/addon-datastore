# Submission Guide
Submitted add-ons should comply with the [NVDA code of conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md).

If your add-on was hosted on [addonFiles](https://github.com/nvaccess/addonFiles) please read the [migrating to datastore guide](./migratingFromAddonFiles.md).

## Background
Submitting an add-on version is done via a GitHub issue form.
A JSON metadata file is generated from the issue form and the add-on's manifest.
A detailed description of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
When the issue form is submitted, the JSON file is generated and submitted as a pull request to the repository.

Automated validation checks are run against the pull request.
If there are validation errors, they will be commented on the pull request.
Otherwise, the pull request will be merged, the issue will be closed and the add-on will become available in the Add-on Store.

## Approval process
Publishers must be approved to submit add-ons, on a per add-on basis.
If you do not maintain the submitted add-on's repository, it is expected that you have authorisation to publish the add-on from the authors.

If you submit many add-ons you may be granted trusted submitter status, which allows you to publish/submit for all add-ons.
It is expected that trusted submitters do not abuse this process.
Granting and removing trusted submitter status of publishers will be decided and handled entirely by NV Access.

Submitters which abuse the submission process will have their submitter approval revoked.
Please report any issues with submitted add-ons to <info@nvaccess.org>.

## Steps to submit an add-on
1. Select ["Add-on registration" from the new issue options](https://github.com/nvaccess/addon-datastore/issues/new/choose).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission, and generate a pull request to submit your add-on to the store.
1. If this is your first submission of this add-on, manual approval will be required to be added to the approved submitters list for the add-on.
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
