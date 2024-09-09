const glob = require('glob');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const { exec } = require('child_process');

function removeMetadataFile({core}, metadataFile) {
  exec(`rm "${metadataFile}"`, (err, stdout, stderr) => {
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
    if (stderr !== '' || err !== null) {
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      console.error(`Failed to delete downloaded add-on file for ${metadataFile}`);
      return;
    }
  })
}

function checkDownloadedAddonHash({core}, downloadFileName, sha256) {
  // if hash mismatches, delete the addon data file
  const hash = crypto.createHash('sha256');
  hash.write("")
  hash.setEncoding('hex');
  const fileStream = fs.createReadStream(downloadFileName);
  fileStream.on('data', chunk => {
    hash.update(chunk);
  });
  fileStream.on('end', () => {
    const fileHash = hash.digest('hex');
    hash.end();
    // delete downloaded file
    removeDownloadedAddonFile(downloadFileName, metadataFile);
    if (fileHash.toLowerCase() !== sha256.toLowerCase()) {
      console.log(`Hash mismatch: ${fileHash} !== ${sha256}, deleting file "${metadataFile}"`);
      removeMetadataFile({core}, metadataFile);
      return;
    }
  });
}

function checkMetadataDownloadResult({core}, metadataFile, downloadFileName, sha256, err, stdout, stderr) {
  if (stderr !== '' || err !== null) {
    console.log(`err: ${err}`);
    console.log(`stdout: ${stdout}`);
    console.log(`stderr: ${stderr}`);
    // delete file if download failed
    removeMetadataFile({core}, metadataFile);
    return;
  }

  checkDownloadedAddonHash({core}, downloadFileName, sha256);
}

function checkMetadataFile({core}, metadataFile) {
  const addonMetadataContents = fs.readFileSync(metadataFile);
  const addonMetadata = JSON.parse(addonMetadataContents);
  const sha256 = addonMetadata.sha256;
  const downloadFileName = `${uuidv4()}.nvda-addon`;
  // if download fails, delete the addon data file
  exec(
    `curl --fail --silent --show-error --location --output "${downloadFileName}" "${addonMetadata.URL}"`,
    // increase maxBuffer size to 10GB
    { maxBuffer: 1024 * 1024 * 1024 * 10 },
    (err, stdout, stderr) => {
      checkMetadataDownloadResult({core}, metadataFile, downloadFileName, sha256, err, stdout, stderr);
  });
}

module.exports = ({core}, globPattern) => {
  const metadataFiles = glob.globSync(globPattern);
  metadataFiles.forEach(metadataFile => {
    checkMetadataFile({core}, metadataFile);
  });
};
