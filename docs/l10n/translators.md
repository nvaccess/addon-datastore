# Translation Guide for Translators

## Overview

Many NVDA add-ons use the [community NVDA Add-ons Crowdin project](https://crowdin.com/project/nvdaaddons) to manage translations.

This project allows translators to contribute both interface translations and documentation translations.

Translations are synchronized back to add-on repositories through the localization workflow provided by the NVDA Add-on Template.

## Joining the Translation Community

Before contributing translations, translators are encouraged to subscribe to the NVDA Translations mailing list.

The mailing list is the primary place for discussing translation-related topics within the NVDA community.

## NVDA Translations Mailing List

The NVDA community maintains the NVDA Translations mailing list on Groups.io.

This mailing list is used to:

* Discuss translation-related topics.
* Request access to translation teams.
* Coordinate translation efforts.
* Report translation issues.
* Discuss problems affecting translation tools or workflows.

Translators are encouraged to subscribe to the mailing list:

https://groups.io/g/nvda-translations

The mailing list is often the best place to ask questions, request access to a translation team, and seek assistance from other translators and project maintainers.

## Joining the Translation Project

To contribute translations:

1. Create a Crowdin account.
1. Subscribe to the NVDA Translations mailing list.
1. Request access to the appropriate translation team if necessary.
1. Join the NVDA Add-ons Crowdin project.
1. Select the language you wish to translate.
1. Begin translating interface strings and documentation.

## Translation Methods

Translations can be performed using either the Crowdin web interface or local translation tools.

### Crowdin Web Editor

Crowdin provides a web-based editor that allows translators to:

* Translate strings online.
* Review existing translations.
* Suggest improvements.
* Vote on translation proposals.

This method does not require any additional software installation.

### Poedit

Many NVDA translators prefer to work locally using [Poedit](https://poedit.com) because of its accessibility and ease of use.

Poedit supports both:

* Portable Object (`.po`) files used for interface translations.
* XLIFF (`.xliff`) files used for documentation translations.

After completing translations locally, files can be uploaded back to Crowdin using `l10nUtil.exe`.

## Translating Interface Strings

Interface translations are stored in Portable Object (`.po`) files.

These files can be translated either:

* Directly in Crowdin.
* Using Poedit.

## Translating Documentation

Documentation translations are stored in XLIFF (`.xliff`) files.

These files are generated automatically from the add-on documentation.

Documentation can be translated:

* Directly in Crowdin.
* Using Poedit.

When translating documentation:

* Translate only the text content.
* Preserve placeholders and formatting.
* Do not modify the XLIFF structure manually.

## Uploading Offline Translations

After translating files locally, they can be uploaded to Crowdin using `l10nUtil.exe`.

This utility is distributed through the `nvdaL10n` project.

Examples:

```bash
l10nUtil.exe uploadTranslationFile fr addonName.po -c addon
```

```bash
l10nUtil.exe uploadTranslationFile fr addonName.xliff -c addon
```

Where:

* `fr` is the Crowdin language code.
* `addonName.po` is a translated interface file.
* `addonName.xliff` is a translated documentation file.

Once uploaded, the translations become available in Crowdin and can later be synchronized back into the add-on repository.

## Using l10nUtil.exe

To display the complete list of available commands:

```bash
l10nUtil.exe --help
```

or:

```bash
l10nUtil.exe -h
```

To display help for a specific command:

```bash
l10nUtil.exe downloadTranslationFile --help
```

or:

```bash
l10nUtil.exe downloadTranslationFile -h
```

Refer to the utility help output for a complete list of supported commands and options.

## How Synchronization Works

Translations are not immediately imported into GitHub repositories.

The add-on maintainer runs a synchronization workflow that:

1. Connects to the NVDA Add-ons Crowdin project.
2. Downloads completed translations.
3. Verifies their translation completion percentage.
4. Synchronizes eligible translations back into the repository.

Depending on the repository configuration, translations may only be synchronized after reaching a minimum completion percentage.

This threshold is controlled by the add-on maintainer.

## Why Has My Translation Not Appeared Yet?

Possible reasons include:

* The synchronization workflow has not yet run.
* The required translation completion percentage has not yet been reached.
* The maintainer has temporarily disabled synchronization.
* The translation was completed after the most recent synchronization cycle.

## Best Practices

To improve translation quality:

* Maintain consistency with existing terminology.
* Preserve placeholders and formatting.
* Review existing translations before introducing new terminology.
* Coordinate with other translators whenever possible.
* Test translated files locally before uploading them when possible.

## Reporting Problems

If you encounter translation issues:

* Contact the add-on maintainer.
* Open an issue in the add-on repository if appropriate.
* Ask for assistance on the NVDA Translations mailing list.
* Discuss translation-related issues with the NVDA translation community.

## Frequently Asked Questions

### Can I translate both documentation and interface strings?

Yes.

The NVDA Add-ons Crowdin project supports both interface translations (`.po`) and documentation translations (`.xliff`).

### Do I need to use the Crowdin web interface?

No.

Many translators work directly in Crowdin, while others prefer to use Poedit and upload their completed translations afterwards using `l10nUtil.exe`.

Both approaches are supported by the NVDA Add-ons translation workflow.

### Do I need access to GitHub?

Not necessarily.

Most translators work exclusively through Crowdin or through local translation tools combined with `l10nUtil.exe`.

The synchronization workflow is managed by the add-on maintainer and automatically imports translations into GitHub repositories.

### Can I force synchronization?

No.

Synchronization is controlled by the add-on maintainer through the localization workflow provided by the NVDA Add-on Template.
