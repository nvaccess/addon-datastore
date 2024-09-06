const glob = require('glob');
const crypto = require('crypto');
const { v4: uuidv4 } = require('uuid');

module.exports = ({core}, globPattern) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  const files = glob.globSync(globPattern);
  files.forEach(file => {
    const addonMetadataContents = fs.readFileSync(file);
    const addonMetadata = JSON.parse(addonMetadataContents);
    const addonId = addonMetadata.addonId;
    const sha256 = addonMetadata.sha256;
    const downloadFileName = `${uuidv4()}.nvda-addon`;
    exec(
      `curl --fail --silent --show-error --location --output "${downloadFileName}" "${addonMetadata.URL}"`,
      // increase maxBuffer size to 10GB
      { maxBuffer: 1024 * 1024 * 1024 * 10 },
      (err, stdout, stderr) => {
      if (stderr !== '' || err !== null) {
        console.log(`err: ${err}`);
        console.log(`stdout: ${stdout}`);
        console.log(`stderr: ${stderr}`);
        // delete file if download failed
        exec(`rm "${file}"`, (err, stdout, stderr) => {
          if (stderr !== '' || err !== null) {
            console.log(`err: ${err}`);
            console.log(`stdout: ${stdout}`);
            console.log(`stderr: ${stderr}`);
            core.setFailed('Failed to delete add-on file');
            return;
          }
        })
        return;
      }
      const hash = crypto.createHash('sha256');
      hash.write("")
      // if hash mismatches, delete the file
      hash.setEncoding('hex');
      const fileStream = fs.createReadStream(downloadFileName);
      fileStream.on('data', chunk => {
        hash.update(chunk);
      });
      fileStream.on('end', () => {
        const fileHash = hash.digest('hex');
        hash.end();
        if (fileHash.toLowerCase() !== sha256.toLowerCase()) {
          console.log(`Hash mismatch: ${fileHash} !== ${sha256}, deleting file "${file}"`);
          exec(`rm "${file}"`, (err, stdout, stderr) => {
            if (stderr !== '' || err !== null) {
              console.log(`err: ${err}`);
              console.log(`stderr: ${stderr}`);
              core.setFailed('Failed to delete add-on file');
              return;
            }
          })
          return;
        }
      })
    });
  });
};
