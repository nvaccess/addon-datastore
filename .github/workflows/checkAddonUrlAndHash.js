const glob = require('glob');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const { exec } = require('child_process');
const PROJECT_URL = "https://github.com/nvaccess/addon-datastore/blob/master/";

function removeMetadataFile({core}, metadataFile, reason) {
  console.log(`Deleting file "${metadataFile}" because ${reason}`);
  // normalise the Windows-style path to be usable for the URL in the PR body
  const metadataFileNormalised = metadataFile.replaceAll('\\', '/');
  core._PRBodyString += `| [${metadataFileNormalised.replace("addons/", "")}](${PROJECT_URL}${metadataFileNormalised}) | ${reason} |\n`;
  core.setOutput("PRBodyString", core._PRBodyString);
  exec(`rm "${metadataFile}"`, (err, stdout, stderr) => {
    // stdout is garbage here, so we don't use it
    if (stderr !== '' || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stderr: ${stderr}`);
      core.setFailed(`Failed to delete add-on file: ${metadataFile}`);
      return;
    }
  })
}

function removeDownloadedAddonFile(downloadFileName, metadataFile) {
  exec(`rm "${downloadFileName}"`, (err, stdout, stderr) => {
    // stdout is garbage here, so we don't use it
    if (stderr !== '' || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stderr: ${stderr}`);
      console.error(`Failed to delete downloaded add-on file for ${metadataFile}`);
      return;
    }
  })
}

function checkDownloadedAddonHash({core}, downloadFileName, metadataFile, sha256) {
  // if hash mismatches, delete the addon data file
  const hash = crypto.createHash('sha256');
  hash.setEncoding('hex');
  const fileStream = fs.createReadStream(downloadFileName);
  fileStream.on('data', chunk => {
    hash.update(chunk);
  });
  fileStream.on('end', () => {
    const fileHash = hash.digest('hex');
    hash.end();
    // Clean up the downloaded file
    removeDownloadedAddonFile(downloadFileName, metadataFile);
    if (fileHash.toLowerCase() !== sha256.toLowerCase()) {
      removeMetadataFile({core}, metadataFile, `Hash mismatch ${fileHash} (actual) != ${sha256} (expected)`);
      return;
    }
  });
}

function checkMetadataDownloadResult({core}, metadataFile, downloadFileName, sha256, err, stdout, stderr) {
  // if download fails, delete the addon metadata file
  if (stderr !== '' || err !== null) {
    console.log(`err: ${err}`);
    console.log(`stdout: ${stdout}`);
    console.log(`stderr: ${stderr}`);
    // strip newlines and carriage returns from stderr to avoid breaking the markdown table
    const strippedStderr = stderr.replaceAll("\n", "  ").replaceAll("\r", "");
    removeMetadataFile({core}, metadataFile, `Download failed: ${strippedStderr}`); 
    return;
  }

  checkDownloadedAddonHash({core}, downloadFileName, metadataFile, sha256);
}

function checkAddonDownload({core}, metadataFile) {
  const addonMetadataContents = fs.readFileSync(metadataFile);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const sha256 = addonMetadata.sha256;
  // We need a unique name otherwise we could overwrite files
  const downloadFileName = `${uuidv4()}.nvda-addon`;
  // if download fails, delete the addon data file
  exec(
    `curl --fail --silent --show-error --location --output "${downloadFileName}" "${addonMetadata.URL}"`,
    // increase maxBuffer size to 10GB as add-on files can be large,
    // and we need to read the entire file to calculate the hash
    { maxBuffer: 1024 * 1024 * 1024 * 10 },
    (err, stdout, stderr) => {
      checkMetadataDownloadResult({core}, metadataFile, downloadFileName, sha256, err, stdout, stderr);
  });
}

module.exports = ({core}, globPattern) => {
  // We want to build a table of files that are being removed
  core._PRBodyString = "| File | Reason |\n|---|---|\n";
  const metadataFiles = glob.globSync(globPattern);
  metadataFiles.forEach(metadataFile => {
    checkAddonDownload({core}, metadataFile);
  });
};
