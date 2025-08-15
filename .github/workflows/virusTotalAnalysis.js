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
  fs.writeFileSync(metadataFile, stringified + "\n");
  // Store the latest vtScanUrl for single file analysis
  core.setOutput("vtScanUrl", vtScanUrl);
}


function getVirusTotalAnalysis({core}, addonMetadata, metadataFile) {
  /*
  Get the VirusTotal analysis for the add-on file.
  Store the results in the metadata file and the scan URL in the add-on metadata file.
  If Virus total fails to scan the add-on, fail the job.
  */
  countAPIUsageAndWait({core});
  exec(`vt file ${addonMetadata.sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
    if (stderr !== "" || err !== null) {
      console.error(`Failed to get VirusTotal analysis for ${metadataFile}, submitting for scanning`);
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      if (core._isSingleFileAnalysis) {
        core.setFailed(`Failed to get VirusTotal analysis for ${metadataFile}`);
      }
      // Resubmit and try again
      virusTotalSubmit({core}, [metadataFile]);
      getVirusTotalAnalysis({core}, addonMetadata, metadataFile);
      return;
    }
    writeVTScanUrl({core}, metadataFile, addonMetadata);
    // Append the VirusTotal analysis to the file for an artifact
    const vtData = JSON.parse(stdout);
    const stats = vtData[0]["last_analysis_stats"];
    const malicious = stats.malicious;
    if (malicious === 0) {
      core.info(`VirusTotal analysis succeeded for ${metadataFile}`);
      return;
    }
    if (addonMetadata.scanResults === undefined) {
      addonMetadata.scanResults = {};
    }
    addonMetadata.scanResults.virusTotal = vtData;
    stringified = JSON.stringify(addonMetadata, null, "\t");
    fs.writeFileSync(metadataFile, stringified + "\n");
    if (core._isSingleFileAnalysis) {
      core.setFailed(`VirusTotal analysis failed for ${metadataFile}`);
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
  // Check if add-on has been submitted before to VirusTotal.
  if (addonMetadata.vtScanUrl === undefined) {
    core.info(`VirusTotal scanning has not been performed for ${metadataFile}`);
    virusTotalSubmit({core}, [metadataFile]);
  }
  // Check if add-on has had results saved before through VirusTotal.
  if (addonMetadata.scanResults !== undefined && addonMetadata.scanResults.virusTotal !== undefined) {
    core.info(`VirusTotal analysis skipped, already performed for ${metadataFile}`);
    return;
  }
  getVirusTotalAnalysis({core}, addonMetadata, metadataFile);
}

module.exports = ({core}, metadataFiles) => {
  // Count API usages to adhere to rate limiting
  core._apiUsageCount = 0;
  core._isSingleFileAnalysis = metadataFiles.length == 1;
  metadataFiles.forEach(metadataFile => {
    getVirusTotalAnalysisIfRequired({core}, metadataFile);
  });
};
