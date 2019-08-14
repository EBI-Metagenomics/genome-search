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

Use `conda` to manage the virtual env.

Configure the virtual environment: `conda create --name genome-search`.

Activate `conda activate genome-search`.

Install `install-dev.sh`

Export the ENV variables running `source env-variables.sh`.

## Berkley DB.

`Berkley DB` Version 4.8 is not avaiable as a conda package so we must compile it using the gcc installed with conda.

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

NOTE: **The yaml and the index need to be located on the same folder**

## Human genomes data cache

The EMG genomes data is stored locally on a BSB DB.

In order to populate the cache execute: 
`python src/get_genomes.py`

NOTE: Override the env variable `API_URL` to use a custom url.

## Run

Start the process `supervisord` (conf picked from supervisord.conf)

### To stop the server

`kill -s SIGTERM $(cat supervisord.pid)`