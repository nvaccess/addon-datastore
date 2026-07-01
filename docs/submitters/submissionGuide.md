# Submission Guide

Submitted add-ons should comply with the [NVDA code of conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md).

## Background

Submitting an add-on version is done via a [GitHub issue form](https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml).

Publishers must be approved to submit add-ons, on a per add-on basis.
If you do not maintain the submitted add-on's repository, it is expected that you have authorisation to publish the add-on from the authors.
It may take up to 2 weeks for approval for new add-ons.
Once you have been approved to submit an add-on, future updates for the add-on should not require approval.

VirusTotal is used to scan the submitted add-on for malicious content.
If malicious content is detected, the add-on will be left pending until it can be reviewed.
NV Access will determine whether or not the detection should prevent the add-on from being accepted.

Automated validation checks are run against the pull request.
If there are validation errors, they will be commented on the pull request.
Otherwise, the add-on will become available in the Add-on Store.

## Steps to submit an add-on

1. Open the ["Add-on registration" issue form](https://github.com/nvaccess/addon-datastore/issues/new?template=registerAddon.yml).
1. Fill out and submit the issue form.
This will create an issue with a summary of your submission, and generate a pull request to submit your add-on to the store.
1. If this is your first submission of this add-on, manual approval will be required to be added to the approved submitters list for the add-on.
You do not need to do anything if you are the maintainer of the add-on you submitted.
Please wait for an NV Access staff member to review the submission, it may take up to 2 weeks.
1. Automated checks are ran on the pull request to validate the submission.
Refer to [the validation section](#validation) for more information on automated checks.
1. If the checks fail, a comment should be added to the issue outlining the failure.
To address the issues, resubmit the issue form.
You may need to also update your add-on manifest.
Descriptions for the fields of the JSON schema can be found in [jsonMetadata.md](../design/jsonMetadata.md).
1. The checks may fail due to code being flagged as malicious.
Please review the flagged content and consider fixing them or commenting why they are a false positive.
An NV Access staff will review the submission and consider accepting if they believe it is a false positive.
This may take up to 2 weeks.
1. If the checks pass, the pull request should be merged automatically.
The add-on should soon become available in the Add-on Store.

## Validation

The add-on manifest and the submitted information in the issue form must follow certain validation requirements.

### Issue form validation

* All URLs must start with `https://`.
* Download URL is valid:
  * Must start with `https://` and end with `.nvda-addon`.
  * The URL is a direct download link that successfully downloads the `*.nvda-addon` file.
* If the add-on manifest field `lastTestedNVDAVersion` refers to a release currently in beta or alpha, the channel must be set to `beta` or `dev`.
NVDA API versions are listed in [`nvdaAPIVersions.json`](../../transform/nvdaAPIVersions.json).
Those listed as `"experimental": true` mean that add-on API is not finalised for that release yet.
An add-on referring or relying on that API version must be marked as `beta` or `dev`.

### Add-on manifest validation

* The manifest exists in the downloaded `*.nvda-addon` file and can be loaded by the `AddonManifest` class.
* The `name` field:
  * must be unique, other [add-ons already listed](../../addons) must not have a similar name.
  * must consist of only letters, numbers, underscores and hyphens.
* The `version` field must be of the form `major.minor` or `major.minor.patch`.
* The `lastTestedNVDAVersion` and `minimumNVDAVersion` fields are valid NVDA API versions.
These are listed in [`nvdaAPIVersions.json`](../../transform/nvdaAPIVersions.json).
* All URLs must start with `https://`.

## Registering an add-on in the translation system

The [NVDA Add-on Template](https://github.com/nvaccess/addonTemplate) includes built-in support for Crowdin-based translation workflows.

Translation support covers both user interface translations (`.po` files) and documentation translations (`.xliff` files).

Depending on your role, please refer to the appropriate documentation:

* [Translation guide for add-on authors](https://github.com/nvaccess/AddonTemplate/blob/master/docs/l10n/addonAuthors.md): explains how to synchronize translations between the add-on and Crowdin.
* [Translation guide for translators](https://github.com/nvaccess/AddonTemplate/blob/master/docs/l10n/addonTranslators.md): Explains how to contribute translations through Crowdin.
