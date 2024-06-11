module.exports = ({core}) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  const addonMetadataContents = fs.readFileSync('addonMetadata.json');
  const addonMetadata = JSON.parse(addonMetadataContents);
  const addonId = addonMetadata.addonId;
  core.setOutput('addonId', addonId);
  const sha256 = addonMetadata.sha256;
  const analysisUrl = `https://www.virustotal.com/gui/file/${sha256}`;
  console.log(analysisUrl);
  core.setOutput('analysisUrl', analysisUrl);
  const reviewedAddonsContents = fs.readFileSync('reviewedAddons.json');
  const reviewedAddonsData = JSON.parse(reviewedAddonsContents);
  if (reviewedAddonsData[addonId] !== undefined && reviewedAddonsData[addonId].includes(sha256)) {
    core.info('VirusTotal analysis skipped');
    return;
  }
  exec(`vt file ${sha256} -k ${process.env.API_KEY} --format json`, (err, stdout, stderr) => {
    console.log(`err: ${err}`);
    console.log(`stdout: ${stdout}`);
    console.log(`stderr: ${stderr}`);
    const vtData = JSON.parse(stdout);
    fs.writeFileSync('vt.json', stdout);
    const stats = vtData[0]["last_analysis_stats"];
    const malicious = stats.malicious;
    if (malicious === 0) {
      core.info('VirusTotal analysis succeeded');
      return;
    }
    if (reviewedAddonsData[addonId] === undefined) {
      reviewedAddonsData[addonId] = [];
    }
    reviewedAddonsData[addonId].push(sha256);
    stringified = JSON.stringify(reviewedAddonsData, null, 2);
    fs.writeFileSync('reviewedAddons.json', stringified);
    core.setFailed('VirusTotal analysis failed');
  });
};
