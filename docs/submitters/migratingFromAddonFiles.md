# Migrating from addonFiles to addon-datastore
Add-ons which used to be registered in the [addonFiles repository](https://github.com/nvaccess/addonFiles) are made available through [a legacy endpoint](https://github.com/nvaccess/addon-datastore/blob/master/docs/design/designOverview.md#legacy).
The [legacy community add-ons website](https://addons.nvda-project.org/) is dependent on this endpoint.
Other consumers may also be dependent on this endpoint.

When migrating to the new add-on datastore, publishers may wish to update their add-on ID, instead of using the one registered in addonFiles.

## Updating legacy add-on IDs

#### Updating casing to lowerCamelCasing
The legacy endpoint is case-insensitive, meaning authors can easily update the casing in the new add-on datastore.
Just open a pull request changing the casing of the add-on ID folder name,
and the add-on ID for all the submission files in the folder.

#### Renaming add-on ID
1. [Submit the new add-on to this repository](./submissionGuide.md).
1. Update the [community add-ons website](https://addons.nvda-project.org/) to use the new add-on ID.
1. Consider deleting the legacy add-on submission in this repository.
