module.exports = ({github, core}, path) => {
  const fs = require('fs');
  const addonMetadataContents = fs.readFileSync('addonMetadata.json');
  const addonMetadata = JSON.parse(addonMetadataContents);
  const addonId = addonMetadata.addonId;
  const sha256 = addonMetadata.sha256;
  const reviewedAddonsContents = fs.readFileSync('reviewedAddons.json');
  const reviewedAddonsData = JSON.parse(reviewedAddonsContents);
  if (reviewedAddonsData.addonId !== undefined && reviewedAddonsData.addonId.includes(sha256)) {
    core.info('Analysis skipped');
   return
  }
  const contents = fs.readFileSync(path);
  const data = JSON.parse(contents);
  const runs = data.runs[0];
  const results = runs.results;
  if (results.length === 0) {
    core.info("Security analysis succeeded");
  } else {
    if (reviewedAddonsData.addonId === undefined) {
      reviewedAddonsData.id = [];
	}
    reviewedAddonsData.addonId.push(sha256);
    const stringified = JSON.stringify(reviewedAddonsData, null, 2);
    fs.writeFileSync('reviewedAddons.json', stringified);
    core.setFailed("Security analysis failed");
  }
};
