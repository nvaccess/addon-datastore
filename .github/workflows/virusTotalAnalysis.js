const glob = require("glob");
const fs = require("fs");
const { exec } = require("child_process");
const countAPIUsageAndWait = require("./virusTotalAPISleepAndCount");
const virusTotalSubmit = require("./virusTotalSubmit");


function writeVTScanUrl({core}, metadataFile, addonMetadata) {
  const vtScanUrl = `https://www.virustotal.com/gui/file/${addonMetadata.sha256}`;
  addonMetadata.vtScanUrl = vtScanUrl;
  stringified = JSON.stringify(addonMetadata, null, "\t");
  // Write vtScanUrl to add-on metadata file
  fs.writeFileSync(metadataFile, stringified);
  // Store the latest vtScanUrl for single file analysis
  core.setOutput("vtScanUrl", vtScanUrl);
}


function getVirusTotalAnalysis({core}, addonMetadata, metadataFile, reviewedAddonsData) {
  /*
  Get the VirusTotal analysis for the add-on file.
  If the add-on is flagged as malicious, store the sha256 hash in reviewedAddons.json.
  Always store the scan URL in the add-on metadata file.
  If Virus total fails to scan the add-on, fail the job.
  */
  countAPIUsageAndWait({core});
  exec(`vt file ${addonMetadata.sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
    if (stderr !== "" || err !== null) {
      console.error(`Failed to get VirusTotal analysis for ${addonMetadata.addonId}, submitting for scanning`);
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      if (core._isSingleFileAnalysis) {
        core.setFailed("Failed to get VirusTotal analysis");
      }
      virusTotalSubmit({core}, metadataFile);
      getVirusTotalAnalysis({core}, addonMetadata, metadataFile, reviewedAddonsData);
      return;
    }
    writeVTScanUrl({core}, metadataFile, addonMetadata);
    // Append the VirusTotal analysis to the file for an artifact
    const vtData = JSON.parse(stdout);
    fs.appendFileSync("vt.json", stdout);
    const stats = vtData[0]["last_analysis_stats"];
    const malicious = stats.malicious;
    if (malicious === 0) {
      core.info("VirusTotal analysis succeeded");
      return;
    }
    if (reviewedAddonsData[addonMetadata.addonId] === undefined) {
      reviewedAddonsData[addonMetadata.addonId] = [];
    }
    reviewedAddonsData[addonMetadata.addonId].push(addonMetadata.sha256);
    stringified = JSON.stringify(reviewedAddonsData, null, "\t");
    fs.writeFileSync("reviewedAddons.json", stringified);
    if (core._isSingleFileAnalysis) {
      core.setFailed("VirusTotal analysis failed");
    }
  });
}


function getVirusTotalAnalysisIfRequired({core}, metadataFile) {
  /*
  If we have scanned and stored the VirusTotal analysis for the add-on before,
  skip the analysis. Otherwise, get the VirusTotal analysis and store the URL
  in the add-on metadata.
  */
  const addonMetadataContents = fs.readFileSync(metadataFile);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const addonId = addonMetadata.addonId;
  const reviewedAddonsContents = fs.readFileSync("reviewedAddons.json");
  const reviewedAddonsData = JSON.parse(reviewedAddonsContents);
  // Check if add-on has been flagged before through VirusTotal.
  if (reviewedAddonsData[addonId] !== undefined && reviewedAddonsData[addonId].includes(sha256)) {
    core.info("VirusTotal analysis skipped, already performed");
    return;
  }
  // Check if add-on has been scanned before through VirusTotal.
  if (addonMetadata.vtScanUrl !== undefined) {
    core.info("VirusTotal analysis skipped, already performed");
    return;
  }
  getVirusTotalAnalysis({core}, addonMetadata, metadataFile, reviewedAddonsData);
}

module.exports = ({core}, globPattern) => {
  var metadataFiles = glob.globSync(globPattern);
  // Count API usages to adhere to rate limiting
  core._apiUsageCount = 0;
  core._isSingleFileAnalysis = metadataFiles.length == 1;
  metadataFiles.forEach(metadataFile => {
    getVirusTotalAnalysisIfRequired({core}, metadataFile);
  });
};
