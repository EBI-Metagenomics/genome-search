# BIGSI metagenomics search

Web and API built on top of [Bigsi](https://github.com/Phelimb/BIGSI).

## Purpose

Provide an interface for users to do quick searchs against microbiomes (the human gut at the moment).

## Tech stack

### Front-end 

Based on `jquery` and some plugins. Built using `webpack`.

### Back-end

Based on:
- `Bigsi` (and `BerkleyDB`).
- `Hug` as the Http API provider and `uWSGI` for production.
- `nginx` as a proxy with the API and to server static files.

## Local dev.

### Front-end

Install packages: `npm install`

### Back-end

Configure a python virtual environment: `virtualenv -p python3 venv` and install the requeriments `pip install -r requeriments.txt`

Run `init.sh` to install `BerkleyDB`.

Export the ENV variables running `source env-variables.sh`, this will export:
- `export HUMAN_GUT_CONF="$(pwd)/data/human-gut/human-gut.yaml`
- `export BERKELEYDB_DIR="$(pwd)/data/berkeley_db` for the `BerkleyDB`

Dev env. served by `Hug` directly.

### Dev server

Run `npm run serve`

## Testing

PENDING