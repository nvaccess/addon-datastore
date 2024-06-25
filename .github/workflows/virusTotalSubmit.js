const glob = require('glob');

module.exports = ({core}, globPattern) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  var files = glob.globSync(globPattern);
  const apiUsageCount = 0;
  files.forEach(file => {
    const addonMetadataContents = fs.readFileSync(file);
    const addonMetadata = JSON.parse(addonMetadataContents);
    const addonId = addonMetadata.addonId;
    const sha256 = addonMetadata.sha256;
    if (apiUsageCount >= 200) {
      core.info('VirusTotal API usage limit reached');
      return;
    }
    apiUsageCount++;
    exec(`vt file ${sha256} -k ${process.env.VT_API_KEY} --format json`, (err, stdout, stderr) => {
      if (stderr === '' || err === null || addonMetadata.vtScanUrl !== undefined) {
        // File has been scanned before
        return;
      }
      console.log(`err: ${err}`);
      console.log(`stdout: ${stdout}`);
      console.log(`stderr: ${stderr}`);
      // download add-on file
      exec(`curl --location --output ${addonId}.nvda-addon "${addonMetadata.URL}"`, (err, stdout, stderr) => {
        if (stderr !== '' || err !== null) {
          console.log(`err: ${err}`);
          console.log(`stdout: ${stdout}`);
          console.log(`stderr: ${stderr}`);
          core.setFailed('Failed to download add-on file');
          return;
        }
        // scan downloaded file
        apiUsageCount++;
        exec(`vt scan file -k ${process.env.VT_API_KEY} ${addonId}.nvda-addon`, (err, stdout, stderr) => {
          if (stderr !== '' || err !== null) {
            console.log(`err: ${err}`);
            console.log(`stdout: ${stdout}`);
            console.log(`stderr: ${stderr}`);
            core.setFailed('Failed to scan add-on file');
            return;
          }
        })
      })
    });
  });
};
