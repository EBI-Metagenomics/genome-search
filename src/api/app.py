import os
import re
import sys
from functools import lru_cache

import hug
import yaml

# Monkey patch rocksdb
sys.modules['rocksdb'] = __import__('rocksdb_fake')
from bigsi.graph import BIGSI

MAX_LEN = 5000
MIN_LEN = 50


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
            sample_name
            percent_kmers_found
            num_kmers
            num_kmers_found
        } 
    :rtype: dict
    """
    fasta_seq = _clean_fasta(seq)

    if len(fasta_seq) > MAX_LEN or len(fasta_seq) < MIN_LEN:
        raise ValueError(f'The sequence should be longer that {MIN_LEN} and shorter than {MAX_LEN}kb')

    bigsi = BIGSI(_get_config())
    results = bigsi.search(fasta_seq, threshold, score)
    return {
        'query': fasta_seq,
        'threshold': threshold,
        'results': results
    }

@hug.not_found()
def not_found_handler():
    return 'Not Found'
