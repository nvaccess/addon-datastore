# Translation Guide for Add-on Authors

## Overview

The [NVDA Add-on Template](https://github.com/nvaccess/addonTemplate) includes a complete localization workflow based on GitHub Actions and Crowdin.

The workflow is implemented by:

* `.github/workflows/crowdinL10n.yml`
* Files contained in `.github/scripts`

and is designed to synchronize translations between an add-on repository and the NVDA Add-ons Crowdin project (`nvdaaddons`).

The workflow supports both:

* Interface translations (`.po` files)
* Documentation translations (`.xliff` files)

This allows translators to work entirely within Crowdin while keeping translations synchronized with GitHub automatically.

## How the Workflow Works

The localization workflow performs the following operations:

1. Generate/update source files (.pot and .xliff).
1. Upload source files to Crowdin.
1. Download translated files (.po and .xliff) from Crowdin.
1. Check translation completion percentages.
1. Processing translations (this includes the conversion of .xliff to .md files.).
1. Synchronize eligible translations (.po and md files) back to the add-on repository.

Translation synchronization is performed by `crowdinSync.ps1`.

Before importing a translation, the workflow verifies whether the translation has reached the configured completion threshold.

## GitHub Configuration

To allow the workflow to communicate with Crowdin, the following GitHub secret must be configured:

* `CROWDIN_TOKEN`

This token is used by the synchronization workflow to access the Crowdin API.

By default, the workflow uses the [community NVDA Add-ons Crowdin project](https://crowdin.com/project/nvdaaddons).

Advanced users may configure a different Crowdin project using the variables documented in the AddonTemplate README.

## Translation Completion Threshold

The workflow supports an optional repository variable:

```text
MIN_PERCENTAGE_TRANSLATED
```

This variable defines the minimum translation completion percentage required before a translated file is synchronized back to the repository.

Examples:

* `50` — import files that are at least 50% translated.
* `75` — import files that are at least 75% translated.
* `100` — import only fully translated files.

If the variable is not defined, the workflow uses a default value of:

```text
50
```

## Translation Validation

Before a translation is imported, the workflow queries Crowdin to determine the translation completion percentage.

This validation is performed by:

```text
.github/scripts/checkTranslation.py
```

The script retrieves translation progress information from Crowdin and returns the completion percentage for the file being processed.

The workflow then compares this value with `MIN_PERCENTAGE_TRANSLATED`.

Only translations meeting or exceeding the configured threshold are synchronized back into the add-on repository.

This validation mechanism is applied consistently to both:

* `.po` files
* `.xliff` files

## Running the Workflow

The localization workflow can be executed:

* Automatically through scheduled runs.
* Manually from the GitHub Actions interface.
* Through [GitHub CLI](https://cli.github.com).

Repository maintainers may adjust the workflow schedule if they manage multiple add-ons.

## Reviewing Translation Updates

When translations satisfy the configured threshold, the workflow creates commits containing updated translations.

Maintainers are encouraged to review these changes before including them in a release.

## Troubleshooting

If translations are not synchronized:

* Verify that the workflow completed successfully.
* Verify that the translation completion percentage satisfies the configured threshold.
* Verify that `CROWDIN_TOKEN` is correctly configured.
* Verify that the translation exists in Crowdin.
* Review the workflow logs for synchronization errors.

For additional details, refer to the AddonTemplate localization documentation.
