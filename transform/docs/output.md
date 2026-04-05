# Output

The output for running the transformation is described as follows.
This is written to a given directory that must be new/empty; the transformation creates this directory and fails if it already exists.
Callers are responsible for deleting any previous output directory before running the transformation.

## Output file structure

The following subdirectories and files are created:

- `/addons/addon-1-ID/addonVersion/en.json`
- `/addons/addon-1-ID/addonVersion/ar.json` (when a translation exists)
- `/views/en/NVDA API Version/addon-1-ID/stable.json`
- `/views/en/NVDA API Version/addon-1-ID/beta.json`
- `/views/en/NVDA API Version/addon-2-ID/stable.json`
- `/views/ar/NVDA API Version/addon-1-ID/stable.json`

Examples:

- `/addons/nvdaOCR/2020.3.0/en.json`
- `/views/en/2020.3.0/nvdaOCR/stable.json`

Where `NVDA API Version` may be:

- `2022.1.0`: A major release.
- `2022.1.3`: A patch release.

The system differentiates patch releases from major releases to cater to the (very unlikely) event of requireing a breaking change or introduction to the NVDA add-on API.

## Output file data

Add-on files in `/addons` contain transformed add-on metadata by add-on version and language.
Views in `/views` are relative symlinks to files in `/addons`.

For each required view `(language, NVDA API Version, addon-ID, channel)`, the view symlink points at a single file:

- Prefer exact language translation
- Otherwise prefer language without locale (`pt_BR` -> `pt`)
- Otherwise fallback to `en`

Each transformed add-on file includes all technical details required for NVDA to download, verify file integrity, and install.
It also contains the information necessary for a store entry.

## Output notes

This structure simplifies the processing on the hosting (e.g. NV Access) server.
To fetch the latest add-ons for `<NVDA API Version X>`, the server can concatenate the appropriate JSON files that match a glob: `/views/<lang>/<NVDA API Version X>/*/stable.json`.
Similarly, to fetch the latest version of an add-on with `<Addon-ID>` for `<NVDA API Version X>`, the server can return the data at `/views/<lang>/<NVDA API Version X>/<addon-ID>/stable.json`.
Using the NV Access server as the endpoint for this is important in case the implementation has to change or be migrated away from GitHub for some reason.
