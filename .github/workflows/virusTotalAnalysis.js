const glob = require('glob');

module.exports = ({core}, globPattern) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  var files = glob.globSync(globPattern);
  var apiUsageCount = 0;
  files.forEach(file => {
    const addonMetadataContents = fs.readFileSync(file);
    const addonMetadata = JSON.parse(addonMetadataContents);
    const addonId = addonMetadata.addonId;
    const sha256 = addonMetadata.sha256;
    const vtScanUrl = `https://www.virustotal.com/gui/file/${sha256}`;
    const reviewedAddonsContents = fs.readFileSync('reviewedAddons.json');
    const reviewedAddonsData = JSON.parse(reviewedAddonsContents);
    if (reviewedAddonsData[addonId] !== undefined && reviewedAddonsData[addonId].includes(sha256)) {
      core.info('VirusTotal analysis skipped, already performed');
      return;
    }
    if (addonMetadata.vtScanUrl !== undefined) {
      core.info('VirusTotal analysis skipped, already performed');
      return;
    }
    // Write vtScanUrl to file
    addonMetadata.vtScanUrl = vtScanUrl;
    stringified = JSON.stringify(addonMetadata);
    fs.writeFileSync(file, stringified);
    // Store the latest vtScanUrl for single file analysis
    core.setOutput('vtScanUrl', vtScanUrl);
    if (apiUsageCount >= 200) {
      core.info('VirusTotal API usage limit reached');
      return;
    }
    apiUsageCount++;
    exec(`vt file ${sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
      if (stderr !== '' || err !== null) {
        console.log(`err: ${err}`);
        console.log(`stdout: ${stdout}`);
        console.log(`stderr: ${stderr}`);
        core.setFailed('Failed to get VirusTotal analysis');
        return;
      }
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
  });
  // Sleep 20 seconds to avoid rate limiting
  sleep(20 * 1000);
};
