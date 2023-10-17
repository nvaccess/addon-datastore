module.exports = async ({context, github, core}) => {
  const query = `query($owner:String!, $name:String!) {
    repository(owner:$owner, name:$name){
      id
      discussionCategories(first: 1) {
        nodes {
          id
        }
      }
    }
  }`;
  const variables = {
    owner: context.repo.owner,
    name: context.repo.repo
  }
  const result = await github.graphql(query, variables)
  const repoId = result.repository.id
  core.setOutput('repoId', repoId)
  const catId = result.repository.discussionCategories.nodes[0].id
  core.setOutput('catId', catId)
}
