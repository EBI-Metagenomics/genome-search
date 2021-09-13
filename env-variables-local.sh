#!/bin/bash

export MGYG_CONF="$(pwd)/data/mgyg.yaml"
export BERKELEYDB_DIR="$(pwd)/lib/berkeley_db"
export BERKELEY_VERSION=4.8.30
export LD_LIBRARY_PATH=$BERKELEYDB_DIR/lib
export MGNIFY_CACHE_PATH="$(pwd)/data/mgnify.cache"
