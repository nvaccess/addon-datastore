function sleep(sleepTimeMs) {
    /* Sleep for sleepTimeMs milliseconds.
    Atomics.wait waits a timeout of sleepTimeMs.
    https://stackoverflow.com/a/56406126/8030743
    */
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, sleepTimeMs);
}


module.exports = ({core}) => {
    if (core._apiUsageCount >= Number(process.env.VT_API_LIMIT)) {
        core.info("VirusTotal API usage limit reached");
        core.setFailed("VirusTotal API usage limit reached");
        process.exit(1);
    }
    // Sleep 20 seconds to avoid rate limiting
    sleep(20 * 1000);
    core._apiUsageCount++;
}
