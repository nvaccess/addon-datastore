# transformAddonDataToViews
This repository primarily exists to transform data from [nvaccess/addon-store-submission:master](https://github.com/nvaccess/addon-store-submission) to views located at [nvaccess/addon-store-submission:views](https://github.com/nvaccess/addon-store-submission/tree/views).

## Overview

For each version of NVDA, the meta-data of the most recent (the highest version number) of each Addon is automatically
added, based on the data in `addon-store-submission`.

## Setup
```sh
pip install -r requirements.txt
```

## Usage
```
python -m src.transform {nvdaVersionsPath} {inputPath} {outputPath} [logLevel]
```

### nvdaVersionsPath
A path to the NVDAVersions, see the schema: `src\validate\NVDAVersions_schema.json` and current values `NVDAVersions.json`.
This is an array of NVDA Versions, which include their NVDA API Version, and what API Version they are backwards compatible to.
This allows us to list which versions an addon is compatible for.

### inputPath
Expects a directory.

#### Input file structure
As this repo consumes data from `nvaccess/addon-store-submission`, see [nvaccess/addon-store-submission README layout](https://github.com/nvaccess/addon-store-submission/blob/master/README.md#layout).

#### Input file data
The expected input schema for each file can be found at [nvaccess/validateNvdaAddonMetadata](https://github.com/nvaccess/validateNvdaAddonMetadata/blob/main/_validate/addonVersion_schema.json).

### outputPath
Expects a directory.
- WARNING: Deletes all json data from the directory.
   - This is so new data can be loaded.

Writes the output data to this directory.
[Output documentation](./docs/output.md) describes how the data is structured and what it is used for.

## Run linting and tests
[Tox](https://tox.readthedocs.io/) configures the environment, runs the tests and linting.

```sh
tox
```

## Validating data files

Data files can be validated using the following script:
```sh
python -m src.validate {pathToSchema} {pathToDataFile}
```

### Supported NVDA versions

The transformation creates views using NVDA API Versions, as this will cover all releases of NVDA.
Older versions of NVDA won't have the add-on store built in, but this data can be be browsed or rehosted elsewhere for earlier NVDA versions.

For NVDA versions older than NVDA 2019.3, the NVDA API version is `0.0.0`.
The next API version introduced was 2019.3 in the [NVDA commit 
`899528849792e79b97d67de179f7473cee06b849`](https://github.com/nvaccess/nvda/commit/899528849792e79b97d67de179f7473cee06b849).

`NVDAVersions.json` serves as source of truth for the NVDA versions and NVDA API versions supported by the views transformation.

To validate this file, run the following:
```sh
python -m src.validate src/validate/NVDAVersions_schema.json NVDAVersions.json
```
