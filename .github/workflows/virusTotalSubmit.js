const glob = require("glob");
const { v4: uuidv4 } = require("uuid");
const fs = require("fs");
const { exec } = require("child_process");
const countAPIUsageAndWait = require("./virusTotalAPISleepAndCount");


function submitAddon({core}, addonMetadata, downloadFileName) {
  /*
  Submit add-on file to VirusTotal for scanning.
  Removes downloaded add-on file after scanning.
  Later we will confirm the virus scan results with another API call.
  If add-on submission fails we will continue.
  */
  countAPIUsageAndWait({core});
  // scan downloaded file
  exec(
    `vt scan file -k ${process.env.VT_API_KEY} ${downloadFileName}`,
    // increase maxBuffer size to 10GB as add-on files can be large
    { maxBuffer: 1024 * 1024 * 1024 * 10 },
    (err, stdout, stderr) => {
    removeDownloadedAddonFile(downloadFileName, addonMetadata.URL);
    if (stderr !== "" || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      console.error(`Failed to scan add-on file: ${addonMetadata.URL}`);
      return;
    }
  })
}


function removeDownloadedAddonFile(downloadFileName, metadataFile) {
  exec(`rm "${downloadFileName}"`, (err, stdout, stderr) => {
    // stdout is garbage here, so we don't use it
    if (stderr !== "" || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stderr: ${stderr}`);
      console.error(`Failed to delete downloaded add-on file for ${metadataFile}`);
      return;
    }
  })
}


function downloadAndSubmitAddon({core}, addonMetadata) {
  /*
  Download add-on file to send to VirusTotal for scanning.
  Removes downloaded add-on file after scanning.
  Later we will confirm the virus scan results with another API call.
  If add-on download or submission fails we will continue.
  */
  // We need a unique name otherwise we could overwrite files
  const downloadFileName = `${uuidv4()}.nvda-addon`;
  exec(
    `curl --fail --silent --show-error --location --output "${downloadFileName}" "${addonMetadata.URL}"`,
    // increase maxBuffer size to 10GB as add-on files can be large
    { maxBuffer: 1024 * 1024 * 1024 * 10 },
    (err, stdout, stderr) => {
    if (stderr !== "" || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      console.error(`Failed to download add-on file: ${addonMetadata.URL}`);
      return;
    }
    submitAddon({core}, addonMetadata, downloadFileName);
  })
}


function submitAddonIfNotScanned({core}, metadataFile) {
  /*
  Check if add-on has been scanned before through VirusTotal.
  If not, download and submit the add-on.
  */
  const addonMetadataContents = fs.readFileSync(metadataFile);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const sha256 = addonMetadata.sha256;
  countAPIUsageAndWait({core});
  // Check if file has been scanned before
  exec(`vt file ${sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
    core.debug(`stdout: ${stdout}`);
    core.debug(`stderr: ${stderr}`);
    core.debug(`err: ${err}`);
    try {
      const vtData = JSON.parse(stdout);
      core.debug(`Add-on file ${metadataFile} already submitted, results: ${vtData}`);
      return;
    } catch (e) {
      core.debug(`Add-on file ${metadataFile} has not been scanned before`);
      // File has not been scanned before,
      // download and submit add-on file
      downloadAndSubmitAddon({core}, addonMetadata);
    }
  });
}


module.exports = ({core}, globPattern) => {
  const metadataFiles = glob.globSync(globPattern);
  // Count API usages to adhere to rate limiting
  core._apiUsageCount = 0;
  metadataFiles.forEach(metadataFile => {
    submitAddonIfNotScanned({core}, metadataFile);
  });
};
