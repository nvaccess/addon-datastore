module.exports = ({core}, addonMetadataPath, resultsPath) => {
  const fs = require('fs');
  const addonMetadataContents = fs.readFileSync(addonMetadataPath);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const contents = fs.readFileSync(resultsPath);
  const data = JSON.parse(contents);
  const runs = data.runs[0];
  const results = runs.results;
  if (addonMetadata.scanResults === undefined) {
    addonMetadata.scanResults = {};
  }
  core.setOutput("codeQLResults", results);
  if (results.length === 0) {
    core.info("Security analysis succeeded");
  } else {
    core.setFailed("Security analysis failed");
  }
};
