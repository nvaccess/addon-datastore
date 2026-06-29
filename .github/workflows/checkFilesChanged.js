module.exports = getAddonFileName
const fs = require("fs")

function getAddonFileName(changedFiles) {
	var addonFileName
	for (fileData of changedFiles) {
		const filename = fileData.filename
		var errMsg
		if (filename.startsWith("addons")) {
			if (Boolean(addonFileName)){
				throw "Multiple add-on files updated."
			}
			if (fileData.status != "added") {
				errMsg = "This is a resubmission of a previously submitted add-on version. This add-on version is already available in the Add-on Store. Please submit a new add-on version instead of modifying an existing one."
				// Ensure an error message is passed on to the user when this happens.
				fs.writeFileSync("./validationErrors.md", errMsg)
				throw errMsg
			}
			addonFileName = filename
		}
		else {
			throw "Non-addon-submission files updated."
		}
	}
	return addonFileName
}

