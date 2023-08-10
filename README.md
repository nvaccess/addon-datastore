# Add-on Store

The addon-datastore repository is a data pipeline of submitting, validating and transforming add-on data to views.
These views are hosted on the NV Access server and are available in the NVDA Add-on Store.

Please note: the NVDA project including the Add-on Store has a [Citizen and Contributor Code of Conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md).
NV Access expects that all contributors and other community members will read and abide by the rules set out in this document while participating in the project or contributing add-ons.

### Guide for submitters
Add-on authors who wish to have their add-on distributed through the Add-on Store should refer to [the submission guide](./docs/submitters/submissionGuide.md).

### Design overview
For an overview of the whole Add-on Store, read [the design overview](./docs/design/designOverview.md).

### About security 
Ensuring that an add-on is safe to run is a difficult challenge that isn't addressed here.
However, the metadata for a new submission (add-on release) can be confirmed to match its manifest description.
Additionally, add-on file integrity can be enforced via a SHA256 checksum.
The checksum allows NVDA to ensure that add-on releases are immutable.

### Human review process / code audit
- NV Access doesn't require a manual review of the add-on (code or user experience) itself before the add-on submission.
- NV Access manually maintains a list of approved submitters with permission to submit an add-on to the store
- You are welcome to review code / UX of add-ons and provide that feedback directly to add-on authors.
- The SHA256 checksum of the `.nvda-addon` prevents undetected changes.
- Add-ons should comply with the [NVDA code of conduct](https://github.com/nvaccess/nvda/blob/master/CODE_OF_CONDUCT.md).
Add-ons which are malicious or otherwise break the code of conduct can be removed by:
  - Opening a pull request to remove the submitted add-on metadata
  - Sending an email to <info@nvaccess.org>

### Non-exclusivity
This system does not restrict add-on authors from developing, publishing, and distributing an add-on outside this store.
NVDA will still allow local installation from a `*.nvda-addon` file.
The data hosted here is distributed under the [ODC-PDDL](https://opendatacommons.org/licenses/pddl/1-0/) license.
A plain language summary can be found [here](https://opendatacommons.org/licenses/pddl/summary/).
