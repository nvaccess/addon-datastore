# Testing

To test the submission process from end-to-end, you need to fork the repository and submit sample issues there.

## Setup

1. Create a fork from `nvaccess/addon-datastore` named `nvaccess/test-addon-datastore-[testName]`
1. Configure the fork

   * Enable GitHub Actions
      * Allow GitHub Actions to create and approve pull requests
      * Give GitHub Actions read and write permissions.
   * Enable GitHub Issues
      * Add the label `autoSubmissionFromIssue`
   * Enable GitHub Discussions
      * Create a Discussion Category called: "Add-on Reviews"
   * Create the following deploy environments.
   Ensure they both block on your review.
      * `securityReview`
      * `submitterReview`
   * (Optional) For testing VirusTotal scanning, set the following environment keys:
      * Secret: `VT_API_KEY`.
      Generate your own using VirusTotal.
      If not supplied, add-ons won't be scanned.
      * Variable: `VT_API_LIMIT`.
      Change if necessary to scan a larger batch of add-ons to push daily API limits.

1. Add it as a remote to your `addon-datastore` local git copy:

   * `git remote add testRemoteName https://github.com/nvaccess/test-addon-datastore-testName.git`

1. (Force) push the branch to your test repository

   * `git push testRemoteName testBranch:master`

## Testing submissions

Once the repository is set up, you should be able to create sample add-on submissions.
You can use current pending submissions or past rejected add-ons as examples.

You may need to change your submitter status in `submitters.json` to test the workflow properly.

Pushing to views once an add-on submission has been merged is currently not supported.
This means the "transform to views" step will always fail.
In future we can create a throwaway staging branch in the main repo, which can be used for testing this step.
