module.exports = ({core}, resultsPath) => {
  const fs = require('fs');
  const contents = fs.readFileSync(resultsPath);
  const data = JSON.parse(contents);
  const runs = data.runs[0];
  const results = runs.results;
  core.setOutput("codeQLResults", results);
  if (results.length === 0) {
    core.info("Security analysis succeeded");
  } else {
    core.setFailed("Security analysis failed");
  }
};
