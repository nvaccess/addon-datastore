const glob = require('glob');

function sleep(n) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, n);
}

module.exports = ({core}, globPattern) => {
  const fs = require('fs');
  const { exec } = require('child_process');
  const files = glob.globSync(globPattern);
  var apiUsageCount = 0;
  files.forEach(file => {
    const addonMetadataContents = fs.readFileSync(file);
    const addonMetadata = JSON.parse(addonMetadataContents);
    const addonId = addonMetadata.addonId;
    const sha256 = addonMetadata.sha256;
    if (apiUsageCount >= 200) {
      core.info('VirusTotal API usage limit reached');
      throw new Error('VirusTotal API usage limit reached');
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
        // Sleep 20 seconds to avoid rate limiting
        sleep(20 * 1000);
      })
    });
    // Sleep 20 seconds to avoid rate limiting
    sleep(20 * 1000);
  });
};
