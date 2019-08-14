#!/usr/bin/env bash
set -e
set -u

echo "Starting setup."

# dependencies installation
conda install -y -c conda-forge gcc_linux-64 gcc_impl_linux-64

# bsd db
echo "Installing Berkley DB"

TMP="$(pwd)/tmp"
BERKELEYDB_DIR="$(pwd)/lib/berkeley_db"
BERKELEY_VERSION=4.8.30

wget -P "${TMP}" http://download.oracle.com/berkeley-db/db-"${BERKELEY_VERSION}".tar.gz 
tar -xf "${TMP}"/db-"${BERKELEY_VERSION}".tar.gz -C "${TMP}"
rm -f "${TMP}"/db-"${BERKELEY_VERSION}".tar.gz
cd "${TMP}"/db-"${BERKELEY_VERSION}"/build_unix 
../dist/configure --prefix "$BERKELEYDB_DIR" && make && make install
cd ../../..

echo "Installing dependencies"
# bigsi dependencies that needs compilation, to avoid use conda
conda install -y -c conda-forge mmh3
conda install -y -c anaconda bitarray

# python packages
pip install -r requeriments.txt

echo "Setup completed."