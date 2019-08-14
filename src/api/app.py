import json
import os
import re
import sys
from functools import lru_cache
from operator import itemgetter

import falcon
import hug
import yaml
from bsddb3 import db

# monkey patch rocksdb so we can avoid installing all the dependencies
sys.modules['rocksdb'] = __import__('rocksdb_fake')
from bigsi.graph import BIGSI

MAX_LEN = 5000
MIN_LEN = 50
MGNIFY_CACHE_PATH = os.environ.get('MGNIFY_CACHE_PATH')


def _clean_fasta(seq_string):
    """
    Clean a fasta sequence.
    This will remove the name name of the sequence
    and it will remove any newlines
    """
    if not seq_string:
        return seq_string
    seq_no_header = re.sub('^>.+\n', '', seq_string)
    return re.sub('\n', '', seq_no_header.strip())

@lru_cache()
def _get_config():
    """
    Get the bigsi configuration file
    :returns: The Yaml configuration file for BIGSI
    :rtype: Yaml
    """
    file = os.environ.get('HUMAN_GUT_CONF')
    with open(file, 'r') as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    return config

@hug.post('/search', response_headers={'Access-Control-Allow-Origin': '*'},)
def search(seq: hug.types.text,
           threshold: hug.types.float_number = 0.4,  # bgsi recommendation 
           score: hug.types.smart_boolean = False):
    """
    Search a DNA sequence against the index of the human_gut using BIGSI
    BIGSI stands for: BIGSIs–BItsliced Genomic Signature Indexes.

    :seq: The fasta sequence to be searched on the index.
    :param print_cols: A flag used to print the columns to the console
        (default is False)
    :returns: a dictionary with the original query, threshold and results.
        Thee results is a list of objects with the following structure:
        {
            bigsi: {
                sample_name
                percent_kmers_found
                num_kmers
                num_kmers_found
            },
            mgnify: {
                id,
                attributes: -- MGnify genomes API data  --
            }
        } 
    :rtype: dict
    """
    fasta_seq = _clean_fasta(seq)

    if not re.match('^[ATGCRYMKSWHBVDN\s]+$', fasta_seq, re.IGNORECASE):
        raise falcon.HTTPBadRequest('seq', 'The sequence doesn\'t appear to be a DNA sequence')

    if len(fasta_seq) > MAX_LEN or len(fasta_seq) < MIN_LEN:
        raise falcon.HTTPBadRequest('seq', f'The sequence should be longer that {MIN_LEN} and shorter than {MAX_LEN}pb')

    bigsi = BIGSI(_get_config())

    best_matches = bigsi.search(fasta_seq, threshold, score)
    best_matches = sorted(best_matches, key=itemgetter('percent_kmers_found'), reverse=True)

    # merge the data from the DB
    storage = db.DB()
    storage.open(MGNIFY_CACHE_PATH, None, db.DB_HASH, db.DB_READ_COMMITTED)
    
    results = []

    for hit in best_matches:
        key = hit.get('sample_name')
        data = storage.get(key.encode('utf-8'))
        results.append({
            'mgnify': json.loads(data) if data else {}, 
            'bigsi': hit 
        })

    storage.close()

    return {
        'query': fasta_seq,
        'threshold': threshold,
        'results': results
    }

@hug.not_found()
def not_found_handler():
    return 'Not Found'
