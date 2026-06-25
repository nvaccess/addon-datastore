# Submission Guide

Submitted add-ons should comply with the [NVDA code of conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md).

## Background

Submitting an add-on version is done via a [GitHub issue form](https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml).
A JSON metadata file is generated from the issue form and the add-on's manifest.
A detailed description of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
When the issue form is submitted, the JSON file is generated and submitted as a pull request to the repository.
VirusTotal is used to scan the submitted add-on for malicious content.
NV Access will determine whether or not the detection should prevent the add-on from being accepted.

Automated validation checks are run against the pull request.
If there are validation errors, they will be commented on the pull request.
Otherwise, the pull request will be merged, the issue will be closed and the add-on will become available in the Add-on Store.

## Approval process

Publishers must be approved to submit add-ons, on a per add-on basis.
If you do not maintain the submitted add-on's repository, it is expected that you have authorisation to publish the add-on from the authors.
It may take up to 2 weeks for approval for new add-ons.

## Steps to submit an add-on

1. Open the ["Add-on registration" issue form](https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission, and generate a pull request to submit your add-on to the store.
1. If this is your first submission of this add-on, [manual approval](#approval-process) will be required to be added to the approved submitters list for the add-on.
You do not need to do anything if you are the maintainer of the add-on you submitted.
Please wait for an NV Access staff member to review the submission, it may take up to 2 weeks.
1. Automated checks are ran on the pull request to validate the submission.
Refer to [addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation) for more information on automated checks.
1. If the checks fail, a comment should be added to the issue outlining the failure.
To address the issues, resubmit the issue form.
You may need to also update your add-on manifest.
Descriptions for the fields of the JSON schema can be found in [jsonMetadata.md](./jsonMetadata.md).
1. The checks may fail due to code being flagged as malicious.
Please review the flagged content and consider fixing them or commenting why they are a false positive.
An NV Access staff will review the submission and consider accepting if they believe it is a false positive.
This may take up to 2 weeks.
1. If the checks pass, the pull request should be merged automatically.
The add-on should soon become available in the store.

## Registering an add-on in the translation system

The [NVDA Add-on Template](https://github.com/nvaccess/addonTemplate) includes built-in support for Crowdin-based translation workflows.

Translation support covers both user interface translations (`.po` files) and documentation translations (`.xliff` files).

Depending on your role, please refer to the appropriate documentation:

* [Translation guide for add-on authors](https://github.com/nvaccess/AddonTemplate/blob/master/docs/l10n/addonAuthors.md): explains how to synchronize translations between the add-on and Crowdin.
* [Translation guide for translators](https://github.com/nvaccess/AddonTemplate/blob/master/docs/l10n/addonTranslators.md): Explains how to contribute translations through Crowdin.
