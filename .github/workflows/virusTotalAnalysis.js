const glob = require('glob');
const fs = require('fs');
const { exec } = require('child_process');

function sleep(n) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, n);
}

function countAPIUsageAndWait({core}) {
  // Sleep 20 seconds to avoid rate limiting
  sleep(20 * 1000);
  core._apiUsageCount++;
}

function writeVTScanUrl({core}, metadataFile, addonMetadata) {
  // Write vtScanUrl to file
  const vtScanUrl = `https://www.virustotal.com/gui/file/${addonMetadata.sha256}`;
  addonMetadata.vtScanUrl = vtScanUrl;
  stringified = JSON.stringify(addonMetadata, null, "\t");
  fs.writeFileSync(metadataFile, stringified);
  // Store the latest vtScanUrl for single file analysis
  core.setOutput('vtScanUrl', vtScanUrl);
}

function getVirusTotalAnalysis({core}, addonMetadata, metadataFile, reviewedAddonsData) {
  countAPIUsageAndWait({core});
  exec(`vt file ${addonMetadata.sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
    if (stderr !== '' || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      core.setFailed('Failed to get VirusTotal analysis');
      return;
    }
    writeVTScanUrl({core}, metadataFile, addonMetadata);
    // Append the VirusTotal analysis to the file for an artifact
    const vtData = JSON.parse(stdout);
    fs.appendFileSync('vt.json', stdout);
    const stats = vtData[0]["last_analysis_stats"];
    const malicious = stats.malicious;
    if (malicious === 0) {
      core.info('VirusTotal analysis succeeded');
      return;
    }
    if (reviewedAddonsData[addonMetadata.addonId] === undefined) {
      reviewedAddonsData[addonMetadata.addonId] = [];
    }
    reviewedAddonsData[addonMetadata.addonId].push(addonMetadata.sha256);
    stringified = JSON.stringify(reviewedAddonsData, null, "\t");
    fs.writeFileSync('reviewedAddons.json', stringified);
    core.setFailed('VirusTotal analysis failed');
  });
}

function getVirusTotalAnalysisIfRequired({core}, metadataFile) {
  const addonMetadataContents = fs.readFileSync(metadataFile);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const addonId = addonMetadata.addonId;
  const reviewedAddonsContents = fs.readFileSync('reviewedAddons.json');
  const reviewedAddonsData = JSON.parse(reviewedAddonsContents);
  if (reviewedAddonsData[addonId] !== undefined && reviewedAddonsData[addonId].includes(sha256)) {
    core.info('VirusTotal analysis skipped, already performed');
    return;
  }
  if (apiUsageCount >= 10) {
    core.info('VirusTotal API usage limit reached');
    throw new Error('VirusTotal API usage limit reached');
  }
  getVirusTotalAnalysis({core}, addonMetadata, metadataFile, reviewedAddonsData);
}

module.exports = ({core}, globPattern) => {
  var metadataFiles = glob.globSync(globPattern);
  // Count API usages to adhere to rate limiting
  core._apiUsageCount = 0;
  metadataFiles.forEach(metadataFile => {
    getVirusTotalAnalysisIfRequired({core}, metadataFile);
  });
};
