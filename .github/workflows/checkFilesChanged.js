module.exports = await getAddonFileName()

const url = "GET /repos/nvaccess/addon-datastore/pulls/" + process.env.pullRequestNumber + "/files" 

async function getAddonFileName() {
	const result = await github.request(url)
	var addonFileName
	const changedFiles = result.data
	for (fileData of changedFiles) {
		const filename = fileData.filename
		if (filename.startsWith("addons")) {
			if (Boolean(addonFileName)){
				throw "Please submit addon releases individually. One file at a time."
			}
			if (fileData.status != "added") {
				throw "Modifications to submitted add-ons will not be auto-approved"
			}
			addonFileName = filename
		}
		else {
			throw "Non-addon-submission files updated. This will not be auto-approved."
		}
	}
	return addonFileName
}

