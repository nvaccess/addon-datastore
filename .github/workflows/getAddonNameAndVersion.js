module.exports = ({core}, addonFilename) => {
  const fs = require('fs');
  const contents = fs.readFileSync(addonFilename);
  const metadata = JSON.parse(contents);
  const addonId = metadata.addonId;
  core.setOutput('addonId', addonId);
  const addonName = metadata.displayName;
  core.setOutput('addonName', addonName);
  const addonVersion = metadata.addonVersionName;
  core.setOutput('addonVersion', addonVersion);
};
