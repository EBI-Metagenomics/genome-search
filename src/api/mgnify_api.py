"""
Download all the genomes data from the MGnify API and store it on Berkley DB.
"""
import json

import requests
from bsddb3 import db

API_URL = 'http://localhost:5000/v1/'
BERKLEYDB_PATH = '/home/mbc/projects/bigsi-micro-service/data/mgnify.cache'


def get_data(url, storage):
    """
    Get the genomes DATA from the mgnify API and store it in the
    berkleydb index.
    """
    if url is None:
        return
    
    print('Downloading: ' + url)

    req = requests.get(url)

    # TODO: handle errors
    data = req.json()

    for genome in data.get('data', []):
        # use the accession as the key
        key = genome['id'].strip()
        storage.put(key.encode('utf-8'), json.dumps(genome))

    get_data(data['links']['next'], storage)


if __name__ == '__main__':
    # create if it doesn't exists
    storage = db.DB()
    storage.set_cachesize(1, 0)
    storage.open(BERKLEYDB_PATH, None, db.DB_HASH, db.DB_CREATE)
    
    get_data(API_URL + 'genomes', storage)
    
    storage.close()
