#!/usr/bin/env bash
set -e

# install miniconda
echo "Start build."
VENV_DIR=./venv
rm -rf $VENV_DIR
wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
chmod 755 miniconda.sh
bash ./miniconda.sh -b -p $VENV_DIR -f
rm miniconda.sh
source $VENV_DIR/bin/activate

# make a packable conda env
conda create -n gs
conda activate gs

# dependencies installation
conda update -y conda
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
conda install -y pip
pip install -r requirements.txt

# package conda env for deploy elsewhere
echo "Packaging conda env"
conda install -y conda-pack
conda-pack -n gs --force

echo "Build completed."