The output for running the transformation is described as follows.
This is written to a given directory, and removes existing json data from the directory in the process.

## Output file structure
The following subdirectories and files are created:
- `/NVDA API Version/addon-1-ID/stable.json`
- `/NVDA API Version/addon-1-ID/beta.json`
- `/NVDA API Version/addon-2-ID/stable.json`
eg: `/2020.3.0/nvdaOCR/stable.json`

Where `NVDA API Version` may be:
- `2022.1.0`: A major release.
- `2022.1.3`: A patch release.

The system differentiates patch releases from major releases to cater to the (very unlikely) event of requireing a breaking change or introduction to the NVDA add-on API.

## Output file data
Each addon file is the addon data taken from input that is the latest compatible version, with the given requirements `(NVDA API Version, addon-ID, stable|beta|dev)`.
The transformed data file content will be the same as the input.
The contents for each addon file includes all the technical details required for NVDA to download, verify file integrity, and install.
It also contains the information necessary for a store entry.
Later, translated versions will become available.

## Output notes
This structure simplifies the processing on the hosting (e.g. NV Access) server.
To fetch the latest add-ons for `<NVDA API Version X>`, the server can concatenate the appropriate JSON files that match a glob: `/<NVDA API Version X>/*/stable.json`.
Similarly, to fetch the latest version of an add-on with `<Addon-ID>` for `<NVDA API Version X>`. The server can return the data at `/<NVDA API Version X>/<addon-ID>/stable.json`.
Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated away from GitHub for some reason.
