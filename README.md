[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# COBS metagenomics genome search

Web and API built on top of [COBS](https://github.com/bingmann/cobs).

## Purpose

Search gene fragments against MGnify’s Genome Catalogues (MAGs and Isolates).

## Tech stack
Based on:
- `COBS`
- `Hug` as the Http API provider and CLI interface
- `Docker` for containerisation

Both the API (for handling queries) and CLI (for generating indices) run in a Docker.
This is mostly so that we can build COBS with a good version of cmake, and because the conda and pip packages for COBS
do not contain all of the latest updates.

## Dev setup
### Requirements
You must have Docker or Podman or Singularity installed, as well as Python3.6+ installed.

Install development tools (including pre-commit hooks to run Black code formatting).
```shell
pip install -r requirements-dev.txt
pre-commit install
```

Build the Docker image
```shell
docker build -t mgnify-cobs-genome-search .
```

Invoke the CLI to build an index
```shell
docker run -v $(PWD)/fixtures:/opt/local/data -it mgnify-cobs-genome-search -c index /opt/local/data/catalogues/marine1.0 /opt/local/data/indices/marine1.0
```