module.exports = getAddonFileName
const fs = require('fs')

function getAddonFileName(changedFiles) {
	var addonFileName
	for (fileData of changedFiles) {
		const filename = fileData.filename
		var errMsg
		if (filename.startsWith("addons")) {
			if (Boolean(addonFileName)){
				errMsg = "Please submit addon releases individually. One file at a time."
				fs.writeFile('./validationErrors.md', errMsg, (e) => console.log(e))
				throw errMsg
			}
			if (fileData.status != "added") {
				errMsg = "Modifications to submitted add-ons will not be auto-approved"
				fs.writeFile('./validationErrors.md', errMsg, (e) => console.log(e))
				throw errMsg
			}
			addonFileName = filename
		}
		else {
			errMsg = "Non-addon-submission files updated. This will not be auto-approved."
			fs.writeFile('./validationErrors.md', errMsg, , (e) => console.log(e))
			throw errMsg
		}
	}
	return addonFileName
}

