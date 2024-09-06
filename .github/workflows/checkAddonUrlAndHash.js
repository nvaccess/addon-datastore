const glob = require('glob');
const crypto = require('crypto');
const hash = crypto.createHash('sha256');

module.exports = ({core}, globPattern) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  const files = glob.globSync(globPattern);
  files.forEach(file => {
    const addonMetadataContents = fs.readFileSync(file);
    const addonMetadata = JSON.parse(addonMetadataContents);
    const addonId = addonMetadata.addonId;
    const sha256 = addonMetadata.sha256;
    exec(`curl --location --output ${addonId}.nvda-addon "${addonMetadata.URL}"`, (err, stdout, stderr) => {
      if (stderr !== '' || err !== null) {
        console.log(`err: ${err}`);
        console.log(`stdout: ${stdout}`);
        console.log(`stderr: ${stderr}`);
        // delete file if download failed
        exec(`rm ${file}`, (err, stdout, stderr) => {
          if (stderr !== '' || err !== null) {
            console.log(`err: ${err}`);
            console.log(`stdout: ${stdout}`);
            console.log(`stderr: ${stderr}`);
            core.setFailed('Failed to delete add-on file');
            return;
          }
        })
      }
      // if hash mismatches, delete the file
      hash.setEncoding('hex');
      const fileStream = fs.createReadStream(`${addonId}.nvda-addon`);
      fileStream.on('data', chunk => {
        hash.update(chunk);
      });
      fileStream.on('end', () => {
        const fileHash = hash.digest('hex');
        if (fileHash !== sha256) {
          exec(`rm ${file}`, (err, stdout, stderr) => {
            if (stderr !== '' || err !== null) {
              console.log(`err: ${err}`);
              console.log(`stdout: ${stdout}`);
              console.log(`stderr: ${stderr}`);
              core.setFailed('Failed to delete add-on file');
              return;
            }
          })
        }
      })
    });
  });
};
