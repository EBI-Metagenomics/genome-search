[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Docker Repository on Quay](https://quay.io/repository/microbiome-informatics/genome-search/status "Docker Repository on Quay")](https://quay.io/repository/microbiome-informatics/genome-search)
[![Tests](https://github.com/EBI-Metagenomics/genome-search/actions/workflows/test.yaml/badge.svg?branch=cobs)](https://github.com/EBI-Metagenomics/genome-search/actions/workflows/test.yaml)

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

## Usage
```shell
docker pull quay.io/microbiome-informatics/genome-search
docker run -it quay.io/microbiome-informatics/genome-search
```
_Note that the Quay.io-built image will probably not run on MacOS. You can however build it locally, as below._

## Dev setup
### Requirements
You must have Docker or Podman or Singularity installed, as well as Python3.6+ installed.

Install development tools (including pre-commit hooks to run Black code formatting).
```shell
pip install -r requirements-dev.txt
pre-commit install
```

### Docker build
Build the Docker image
```shell
docker build -t mgnify-cobs-genome-search .
```

### Docker run to use the CLI
Invoke the CLI to build an index (e.g. to rebuild the test fixtures index)
```shell
 docker run -v $(PWD)/tests/fixtures:/opt/local/data -it mgnify-cobs-genome-search -c index create /opt/local/data/catalogues/marine1.0 /opt/local/data/indices/marine1.0 --clobber True
```

And to run a search:
```shell
 docker run -v $(PWD)/tests/fixtures/indices:/opt/local/data -it --env COBS_CONFIG=config/local.yaml mgnify-cobs-genome-search -c search search --seq CATTTAACGCAACCTATGCAGTGTT
TTTCTTCAATTAAGGCAAGTCGAGGCACT --catalogues_filter marine1.0
# 
# {'query': 'CATTTAACGCAACCTATGCAGTGTTTTTCTTCAATTAAGGCAAGTCGAGGCACT', 'threshold': 0.4, 'results': [{'genome': 'MGYG000296002', 'score': 24}]}
```


### Docker run to serve the API
```shell
docker run -v $(PWD)/tests/fixtures/indices:/opt/local/data -v $(PWD)/config/local.yaml:/opt/local/config/local.yaml -p 8000:8000 -it --env COBS_CONFIG=config/local.yaml mgnify-cobs-genome-search
```
If you’re running something else on port 8000 (like the MGnify API), use `-p 8001:8000` instead to expose the COBS API on port 8001 of your machine.

Call the API with a request like:
```shell
curl --location --request POST 'http://127.0.0.1:8001/search' \
--header 'Content-Type: application/json' \
--data-raw '{
    "seq": "CATTTAACGCAACCTATGCAGTGTTTTTCTTCAATTAAGGCAAGTCGAGGCACTATGTAT",
    "catalogues_filter": "marine1.0"
    }'
```

### Running tests
There is a small test suite which runs inside the Docker container. 
A separate `tests/Dockerfile` exists for this purpose.

```shell
docker build -t mgnify-cobs-genome-search-tests -f tests/Dockerfile .
docker run -t mgnify-cobs-genome-search-tests
```

During development/debugging, it is usually convenient to mount the `src/` directory with a volume bind to the docker container, 
e.g. by adding `-v "$(PWD)/src/":"/usr/src/app/src"` to any of the above docker run commands.
This means you do not need to rebuild the docker image every time you change a source file.

## Running in production
This service can be deployed on a webserver using Nginx, Podman, and certbot.
E.g. to set up an Ubuntu 20 VM on [Embassy](https://www.embassycloud.org):

```shell
# Check out the repo using git or the gh cli

# Create a config at /home/ubuntu/cobs/cobs.yaml

# Use podman to run the container
sudo apt update
sudo apt install podman
sudo podman pull quay.io/microbiome-informatics/genome-search:cobs
sudo podman run -e COBS_CONFIG=/home/ubuntu/cobs/cobs.yaml --mount type=bind,source=/home/ubuntu/cobs/,destination=/home/ubuntu/cobs -p 8000:8000 --name cobs --detach quay.io/microbiome-informatics/genome-search:cobs
#  The reason you sudo these commands is that the root user owns a different set of containers to ubuntu.
#  If you pull the image as ubuntu, it won't update the image used by root (systemd) 

# Generate a systemd service to keep podman up
podman generate systemd --new --name cobs > cobs.service
sudo cp cobs.service /etc/systemd/system/
sudo systemctl enable cobs
sudo systemctl start cobs

# Set up nginx
sudo apt install nginx

# Set up certbot for SSL
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx -d cobs-genome-search-01.mgnify.org

# Set up the nginx conf
sudo cp /home/ubuntu/this/repo/path/webserver_configs/nginx.conf /etc/nginx/sites-enabled/default

# Start nginx
sudo service nginx start
```

A [health-check command](https://developers.redhat.com/blog/2019/04/18/monitoring-container-vitality-and-availability-with-podman#what_are_healthchecks_)
might be needed, because sometimes the web service terminates inside the container for myriad reasons.
Just add ` --healthcheck-command 'CMD-SHELL curl http://localhost:8000/search || exit 1' --healthcheck-interval=10s` to the `pomdan run...` command.

### Certificate renewal
If certbot fails to automatically renew the SSL certificate (e.g. because HTTP ingress is limited to a certain CIDR), you can briefly open the firewall and then run: `sudo certbot renew --cert-name cobs-genome-search-01.mgnify.org`
