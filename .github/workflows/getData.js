module.exports = ({context, core}) => {
	// Allow identifying the issue later.
	// setOutput exposes the variable for access at later stages via steps.get-data.outputs
	//
	const issueTitle = context.payload.issue.title
	core.setOutput('issueTitle', issueTitle)
	const issueNumber = context.payload.issue.number
	core.setOutput('issueNumber', issueNumber)
	// Knowing the submitter may be helpful
	// const issueSubmitter = context.payload.sender.login
	//
	// Field headers, Md == Markdown
	const header3Prefix = "###"
	const dlTitleMd = "### Download URL"
	const sourceUrlMd = "### Source URL"
	const publisherMd = "### Publisher"
	const channelMd = "### Channel"
	const licenseMd = "### License Name"
	const licenseUrlMd = "### License URL"
	//
	// collect variables from issue form
	//
	const body = context.payload.issue.body   
	const downloadUrl = body.split(dlTitleMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('downloadUrl', downloadUrl)
	const sourceUrl = body.split(sourceUrlMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('sourceUrl', sourceUrl)
	const publisherUrl = body.split(publisherMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('publisher', publisherUrl)
	const releaseChannel = body.split(channelMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('releaseChannel', releaseChannel)
	const licenseName = body.split(licenseMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('licenseName', licenseName)
	const licenseUrl = body.split(licenseUrlMd)[1].split(header3Prefix)[0].trim()
	core.setOutput('licenseUrl', licenseUrl)
}
