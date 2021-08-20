# BIGSI metagenomics search

Web and API built on top of [Bigsi](https://github.com/Phelimb/BIGSI).

## Purpose

Provide an interface for users to do quick searchs against microbiomes (the human gut at the moment).

## Tech stack

### Back-end

Based on:
- `Bigsi` (and `BerkleyDB`).
- `Hug` as the Http API provider
- `supervisord` and `gunicorn` for production.

## Local environment

### Linux

Use `conda` to manage the virtual env.

Configure the virtual environment: `conda create --name genome-search`.

Activate `conda activate genome-search`.

Install `install-dev.sh`

Export the ENV variables running `source env-variables.sh`.

### Mac

Install bdb using homebrew (includes the magic hacks for this ancient bdb version):

`brew install berkeley-db@4`.

Then use `virtual-env` or `conda`, e.g.:

```shell
conda create --name genome-search python=3.7
pip install -r requirements.txt
```
Most of the environment works the same as on Linux, except Berkeley. So:

```shell
source env-variables.sh
export BERKELEYDB_DIR=/usr/local/opt/berkeley-db@4/
```
(Assuming a typical Homebrew setup.)

### (Optional) Install BIGSI to make indices
Making indices takes a very long time, and makes a very big file (10s of GB).
This is easiest using the prebuilt Docker, and using anaconda.

```shell
conda install -c bioconda mccortex
docker pull phelimb/bigsi
docker run phelimb/bigsi bigsi --help
```
To add to an index:
```shell
mccortex31 build -k 31 -s MGYG-HGUT-00240 -1 dev-data/genomes/MGYG-HGUT-00240/genome/MGYG-HGUT-00240.fna /data/MGYG-HGUT-00240.ctx
docker run --mount type=bind,source="$(pwd)"/data,target=/data phelimb/bigsi bigsi bloom -c /data/berkeleydb.yaml /data/MGYG-HGUT-00240.ctx /data/MGYG-HGUT-00240.bloom
# Make a filepath -> sample name mapping file for BIGSI Build is the easiest way (file path is for inside docker volume)
echo /data/MGYG-HGUT-00240.bloom'\t'MGYG-HGUT-00240 >> data/build_bloom.tsv
docker run --mount type=bind,source="$(pwd)"/data,target=/data bigsi build -f /data/build_bloom.tsv
```

## Berkley DB.

`Berkley DB` Version 4.8 is not available as a conda package so we must compile it using the gcc installed with conda.

This is already taken care by `install.sh` and `install-dev.sh`.

### Dev server

Run `npm run serve`

Dev env. served by `Hug` directly.

Run `hug -f src/api/app.py`

## Production configuration

Install: `install.sh`. This will install conda and all the dependencies.

The yaml structure:

```yaml
h: 1
k: 31
m: 28000000
storage-engine: berkeleydb
storage-config:
  filename: PATH_TO/human-gut.bigsi
  flag: 'r'
```

## Human genomes data cache

The EMG genomes data is stored locally on a BSB DB.

In order to populate the cache execute: 
`python src/get_genomes.py`

NOTE: Override the env variable `API_URL` to use a custom url.

## Run

Start the process `supervisord` (conf picked from supervisord.conf)

### To stop the server

`kill -s SIGTERM $(cat supervisord.pid)`