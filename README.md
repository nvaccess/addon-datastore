# Add-on Store

The addon-datastore repository is a data pipeline of submitting, validating and transforming add-on data to views.
These views are hosted on the NV Access server and will become available in the NVDA add-on store.

The add-on store is a planned NVDA feature, which allows browsing, installing and updating add-ons from within NVDA.
The current work in progress can be tracked in this pull request: https://github.com/nvaccess/nvda/pull/13985

### Guide for submitters
Add-on authors who wish to have their add-on distributed through the add-on store should refer to [the submission guide](./docs/submitters/submissionGuide.md).

### Design overview
For an overview of the whole add-on store, read [the design overview](./docs/design/designOverview.md).

### About security 
Ensuring that an add-on is safe to run is a difficult challenge that isn't addressed here.
However, the metadata for a new submission (add-on release) can be confirmed to match its manifest
description.
Additionally, add-on file integrity can be enforced via a SHA256 checksum.
The checksum allows NVDA to ensure that add-on releases are immutable.

### Human review process / code audit
- NV Access doesn't require a manual review of the add-on (code or user experience) itself before the add-on submission.
- You are welcome to review code / UX of add-ons and provide that feedback directly to add-on authors.
- The SHA256 checksum of the `.nvda-addon` prevents undetected changes.
- User reviews/rating of add-ons are currently out of scope.

### Non-exclusivity
This system does not restrict add-on authors from developing, publishing, and distributing an add-on outside this store.
NVDA will still allow local installation from a `*.nvda-addon` file.
The data hosted here is distributed under the [ODC-PDDL](https://opendatacommons.org/licenses/pddl/1-0/) license.
A plain language summary can be found [here](https://opendatacommons.org/licenses/pddl/summary/).
