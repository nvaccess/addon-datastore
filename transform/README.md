# addon-datastore-transform
This repository primarily exists to transform data from [nvaccess/addon-datastore:master](https://github.com/nvaccess/addon-datastore) to views located at [nvaccess/addon-datastore:views](https://github.com/nvaccess/addon-datastore/tree/views).

## Overview

For each version of NVDA, the meta-data of the most recent (the highest version number) of each add-on is automatically
added, based on the data in `addon-datastore`.

## Setup
```sh
pip install -r requirements.txt
```

## Usage
```
python -m src.transform {nvdaAPIVersionsPath} {inputPath} {outputPath} [logLevel]
```

### nvdaAPIVersionsPath
A path to the nvdaAPIVersions, see the schema: `src\validate\nvdaAPIVersions.schema.json` and current values `nvdaAPIVersions.json`.
This is an array of NVDA API Versions, and what API Version they are backwards compatible to.
This allows us to list which versions an addon is compatible for.

### inputPath
Expects a directory.

#### Input file structure
As this repo consumes data from `nvaccess/addon-datastore`, see [nvaccess/addon-datastore README layout](https://github.com/nvaccess/addon-datastore/blob/master/README.md#layout).

#### Input file data
The expected input schema for each file can be found at [nvaccess/addon-datastore-validation](https://github.com/nvaccess/addon-datastore-validation/blob/main/_validate/addonVersion_schema.json).

### outputPath
Expects a path to a non-existent directory.
Will create the path to that directory.

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

`nvdaAPIVersions.json` serves as source of truth for NVDA API versions supported by the views transformation.

To validate this file, run the following:
```sh
python -m src.validate src/validate/nvdaAPIVersions.schema.json nvdaAPIVersions.json
```
