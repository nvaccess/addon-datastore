module.exports = async ({context, github, core}) => {
  const fs = require('fs')
  const addonVersion = context.steps.getAddonNameAndVersion.outputs.addonVersion
  const contents = fs.readFileSync('discussions.json')
  const data = JSON.parse(contents)
  const addonId = context.steps.getAddonNameAndVersion.outputs.addonId
  const discussionId = data[addonId]["discussionId"]
  console.log(`${discussionId}`)
  const mutation = `mutation {
    addDiscussionComment(
      input: {
        body: "Reviews for version ${addonVersion}",
        discussionId: "${discussionId}",
        clientMutationId: "GitHub Script action"
      }
    ) {
      clientMutationId
      comment {
        url
      }
    }
    }`;
  const response = await github.graphql(mutation)
  const url = response.addDiscussionComment.comment.url
  core.setOutput('url', url)
}
