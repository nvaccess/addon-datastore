module.exports = ({core}, addonMetadataPath, resultsPath, testType) => {
  const fs = require('fs');
  const addonMetadataContents = fs.readFileSync(addonMetadataPath);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const contents = fs.readFileSync(resultsPath);
  const data = JSON.parse(contents);
  const runs = data.runs[0];
  const results = runs.results;
  if (testType !== "errors" && testType !== "warnings") {
    core.setFailed(`Invalid test type: ${testType}`);
  }
  if (addonMetadata.scanResults === undefined) {
    addonMetadata.scanResults = {};
  }
  addonMetadata.scanResults[`codeQL-${testType}`] = results;
  const stringified = JSON.stringify(addonMetadata, null, "\t");
  fs.writeFileSync(addonMetadataPath, stringified + "\n");
  if (results.length === 0) {
    core.info("Security analysis succeeded");
  } else {
    core.setFailed("Security analysis failed");
  }
};
