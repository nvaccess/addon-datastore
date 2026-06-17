# Submission review processes

Guide for processing [pending add-ons](https://github.com/nvaccess/addon-datastore/actions/workflows/sendJsonFile.yml?query=is%3Awaiting).
If add-on needs manual review before processing happens, the submission process will be held, pending approval from NV Access.
This is done using a [deployment environment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments).

Overall process:

1. Go to the [pending add-ons list](https://github.com/nvaccess/addon-datastore/actions/workflows/sendJsonFile.yml?query=is%3Awaiting).
1. Check the pending [deployment environment](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/review-deployments).
    1. If it is `submitterReview` perform [Process for first time submissions](#process-for-first-time-submissions).
    1. If it is `securityReview` perform [Process for flagged add-ons](#process-for-flagged-add-ons).
    1. If it is both, perform both steps.

## Approving an author to submit to a particular add-on ID for the first time

When a GitHub user submits a particular add-on for the first time, the submission is blocked pending initial review from NV Access.
This is to confirm that the GitHub user has authorisation to submit the add-on from the add-on maintainers.
In some cases, 2 separate add-on maintainers may want to lay claim to a single "add-on ID".
It is important for users to expect consistent authorship for a single add-on ID for trust and security reasons.
It would be misleading and potentially risky to be encouraged to update to a fork or alternative add-on without permission from the original maintainers.
See [the submission guide](../submitters/submissionGuide.md#approval-process) for further reasoning behind this.
This registration process ensures a specific add-on ID is only submitted by the same group of authorised maintainers.

### Process for first time submissions

The process for reviewing pending first submissions is as follows:

1. Open the referenced issue and related PR.
1. Check the source code link in the referenced issue.
   * Ensure the submitter matches the repository ownership, or the submitter is a core maintainer for the project.
   If this is not the case, tag the core maintainer in the submission to confirm they give permission for the submission.
   * Check for any obvious red flags with the repository i.e. it doesn't look structured as an add-on, inappropriate content in the readme, author and code only been around for a few days
   * Ensure there is not a clash of add-on IDs by checking [submitters.json](../../submitters.json) for similar IDs.
1. Approve or deny the `submitterReview` deploy environment.
    * If the deployment review request has expired, close the PR and re-run the job.
    * When rejecting, close the associated PR and issue manually, and provide feedback to the author on the issue.

## Approving an add-on which was flagged as malicious

An add-on may be flagged as malicious by VirusTotal.

### Process for flagged add-ons

1. Open the referenced issue and related PR.
1. A comment should appear on the GitHub issue with information on why the add-on was flagged.
1. Consider if the flagged content is a false positive.
This may require discussion within NV Access or with the add-on contributor.
1. Approve or deny the `securityReview` deployment.
    * If the deployment review request has expired, close the PR and re-run the job.
    * When rejecting, close the associated PR and issue manually, and provide feedback to the author on the issue.
