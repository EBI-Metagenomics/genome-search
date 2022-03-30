import logging
import os
import re
from functools import lru_cache
from pathlib import Path

import cobs_index as cobs
import hug
import yaml

KMER_LENGTH = 31

logging.basicConfig(level=logging.DEBUG)


@lru_cache()
def _get_config():
    """
    Get the configuration file
    :returns: The Yaml configuration file for COBS Genome Search
    :rtype: Yaml
    """
    file = os.environ.get("COBS_CONFIG")
    if not (file and Path(file).is_file()):
        logging.warning(
            "No config file set. Using default config. Set COBS_CONFIG to override."
        )
        return {"max_len": 50000, "min_len": 50, "indices": {}}
    with open(file, "r") as infile:
        config = yaml.load(infile, Loader=yaml.FullLoader)
    logging.info(f"Config loaded: {config}")
    return config


@lru_cache()
def _get_searchers():
    """
    Create COBS Search instances for catalogues in the config.
    """
    config = _get_config()
    searchers = {}
    for catalogue, index in config["indices"].items():
        try:
            searchers[catalogue] = cobs.Search(index)
        except Exception as e:
            logging.error(
                f"Could not create COBS Searcher for {catalogue}: {index}. Is the config file incorrect?"
            )
            raise e
    return searchers


def _clean_fasta(seq_string):
    """
    Clean a fasta sequence.
    This will remove the name of the sequence
    and it will remove any newlines
    """
    if not seq_string:
        return seq_string
    seq_no_header = re.sub("^>.+[\n\r]", "", seq_string)
    seq_no_whitespace = re.sub(" +", "", seq_no_header)
    return re.sub("\r\n+", "", seq_no_whitespace.strip())


def _serialize_search_result(search_result: cobs.SearchResult, sequence_length: int):
    num_kmers = sequence_length - KMER_LENGTH + 1
    return {
        "genome": str(search_result.doc_name),
        "num_kmers": num_kmers,
        "num_kmers_found": search_result.score,
        "percent_kmers_found": round(100.0 * search_result.score / num_kmers, 2),
    }


@hug.cli()
@hug.post("/search", response_headers={"Access-Control-Allow-Origin": "*"})
def search(
    seq: hug.types.text,
    threshold: hug.types.float_number = 0.4,
    catalogues_filter: hug.types.multiple = None,
):
    """
    Search a DNA sequence against an index of the MGnify genomes using COBS
    COBS stands for: Compact Bit-sliced Signature Index.

    :param seq: The fasta sequence to be searched on the index.
    :param threshold: Fraction of k-mers that must be present for a match. Default is 0.4
    :param catalogues_filter: List of Genome Catalogue IDs to include genomes from, or None for all.
    :returns: a dictionary with the original query, threshold and results.
        The results is a list of objects with the following structure:
        {
            bigsi: {
                sample_name
                percent_kmers_found
                num_kmers
                num_kmers_found
                #    if score=True in request
                #    ...
                #    score
                #    pvalue
                #    ...
            },
            mgnify: {
                id,
                attributes: -- MGnify genomes API data  --
            }
        }
    :rtype: dict
    """
    fasta_seq = _clean_fasta(seq)
    logging.info("New request")
    logging.info(f"Sequence {fasta_seq}")
    logging.info(f"Threshold {threshold} and catalogues {catalogues_filter}")

    if seq.count(">") > 1:
        logging.info(f'Request rejected, {seq.count(">")} sequences found.')
        raise hug.HTTPBadRequest(
            "seq",
            "Multiple sequences were found, but this is not supported. Please supply a single sequence.",
        )
    if not re.match("^[ATGC]+$", fasta_seq, re.IGNORECASE):
        logging.info(f"Request rejected, non-DNA chars found.")
        logging.info(repr(fasta_seq))
        raise hug.HTTPBadRequest(
            "seq", "The sequence contains characters not expected for a DNA sequence."
        )

    config = _get_config()
    searchers = _get_searchers()

    if len(fasta_seq) > config["max_len"] or len(fasta_seq) < config["min_len"]:
        logging.info(
            f'Request rejected. Length {len(fasta_seq)} out of bounds {config["min_len"]}–{config["max_len"]}'
        )
        raise hug.HTTPBadRequest(
            "seq",
            f"The sequence should be longer that {config['min_len']} and "
            + f"shorter than {config['max_len']}pb",
        )

    matches = []
    for catalogue in catalogues_filter:
        if catalogue not in searchers:
            raise hug.HTTPBadRequest(
                "catalogue_filter", f"Catalogue {catalogue} is not available."
            )
        try:
            matches.extend(searchers[catalogue].search(fasta_seq, threshold))
        except Exception as e:
            logging.error("Caught error from COBS whilst searching", exc_info=e)
            raise hug.HTTPBadRequest(
                "search failed",
                "Your search could not be handled. Did your query contain characters other than ACTG?",
            )
    logging.info(f"Found {len(matches)} matches")
    matches = map(
        lambda match: _serialize_search_result(match, len(fasta_seq)), matches
    )

    return {"query": fasta_seq, "threshold": threshold, "results": list(matches)}


@hug.cli()
def clear_cache():
    """
    Clear the cached config and recreate COBS Search instances.
    Useful if you wish to add a new index without restarting the whole service.
    """
    logging.info("Clearing config cache and recreating COBS searchers")
    _get_config.cache_clear()
    _get_searchers.cache_clear()
    logging.info("New config: " + str(_get_config()))
    logging.info("New searchers: " + str(_get_searchers()))
