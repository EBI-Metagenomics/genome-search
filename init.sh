#!/bin/bash

export TMP="$(pwd)/data/tmp"
export BERKELEYDB_DIR="$(pwd)/data/berkeley_db"
export BERKELEY_VERSION=4.8.30

# Download, configure and install BerkeleyDB
wget -P "${TMP}" http://download.oracle.com/berkeley-db/db-"${BERKELEY_VERSION}".tar.gz 

tar -xf "${TMP}"/db-"${BERKELEY_VERSION}".tar.gz -C "${TMP}"

rm -f "${TMP}"/db-"${BERKELEY_VERSION}".tar.gz

cd "${TMP}"/db-"${BERKELEY_VERSION}"/build_unix 

../dist/configure --prefix "$BERKELEYDB_DIR" && make && make install
