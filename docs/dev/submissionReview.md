
### Approving an author to submit to a particular add-on ID for the first time
When a GitHub user submits a particular add-on for the first time, the submission is blocked pending initial review from NV Access.
This is to confirm that the GitHub user has authorisation to submit the add-on from the add-on maintainers.
In some cases, 2 separate add-on maintainers may want to lay claim to a single "add-on ID".
It is important for users to expect consistent authorship for a single add-on ID for trust and security reasons.
It would be misleading and potentially risky to be encouraged to update to a fork or alternative add-on without permission from the original maintainers.
See [the submission guide](../submitters/submissionGuide.md#approval-process) for further reasoning behind this.
This registration process ensures a specific add-on ID is only submitted by the same group of authorised maintainers.

#### Process
The process for reviewing pending first submissions is as follows:

1. A Pull Request named "Add `GitHubName` as an approved submitter for `addonId`" will be waiting on review.
   - Example: https://github.com/nvaccess/addon-datastore/pull/2674
1. Open the referenced issue
1. Check the source code link in the referenced issue.
   - Ensure the submitter matches the repository ownership, or the submitter is a core maintainer for the project.
   If this is not the case, tag the core maintainer in the submission to confirm they give permission for the submission.
   - Check for any obvious red flags with the repository i.e. it doesn't look structured as an add-on, inappropriate content in the readme, author and code only been around for a few days
1. If it is clear that the submitter has permission to submit the add-on, merge the approval PR.
1. Relabel the original issue with `autoSubmissionFromIssue`
   - i.e. remove the label, save, add the label back, save.
   - This will resubmit the issue.

#### Handling known issues

##### "Create branch" fails
If an issue is mistakenly relabelled twice, the subsequent action may fail at the "Create branch" step.
To fix this:
1. Go to the GitHub action failure and identify the name of the branch where "Create branch" is failing.
1. Go to the [branches for the repository](https://github.com/nvaccess/addon-datastore/branches) and delete the branch.
1. Check if the initial issue has been successfully submitted already.
   - The summary of the GitHub action failure should have a message like "Triggered via issue `x days ago` `@gitHubUserWhoSubmittedOrLabelledTheIssue` labeled `#issueNum` `commitRef`"
   - Confirm that the issue was closed successfully with a matching merged PR
   - Confirm that the add-on version (add-on id and version number) [exists in the repository](https://github.com/nvaccess/addon-datastore/tree/master/addons)
1. If the issue has been submitted correctly, no further action is required.
1. If the issue has not been submitted correctly, relabel the original issue with `autoSubmissionFromIssue`
   - i.e. remove the label, save, add the label back, save.
   - This will resubmit the issue.
