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
				errMsg = "This add-on is already present in the Add-on Store with the same version number.\nPlease submit your add-on with a new version number instead of trying to modify an existing one."
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

