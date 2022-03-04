import logging
import os
import re
from functools import lru_cache
from pathlib import Path

import cobs_index as cobs
import hug
import yaml


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


def _clean_fasta(seq_string):
    """
    Clean a fasta sequence.
    This will remove the name of the sequence
    and it will remove any newlines
    """
    if not seq_string:
        return seq_string
    seq_no_header = re.sub("^>.+\n", "", seq_string)
    return re.sub("\n", "", seq_no_header.strip())


config = _get_config()

searchers = {
    catalogue: cobs.Search(index) for catalogue, index in config["indices"].items()
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
    logging.info(f"New request for sequence {fasta_seq}")
    logging.info(f"Threshold {threshold} and catalogues {catalogues_filter}")

    if seq.count(">") > 1:
        logging.info(f'Request rejected, {seq.count(">")} sequences found.')
        raise hug.HTTPBadRequest(
            "seq",
            "Multiple sequences were found, but this is not supported. Please supply a single sequence.",
        )

    if not re.match("^[ATGCRYMKSWHBVDN\s]+$", fasta_seq, re.IGNORECASE):
        logging.info(f"Request rejected, non-DNA chars found.")
        raise hug.HTTPBadRequest(
            "seq", "The sequence contains characters not expected for a DNA sequence."
        )

    if len(fasta_seq) > config["max_len"] or len(fasta_seq) < config["min_len"]:
        logging.info(
            f'Request rejected. Length {len(fasta_seq)} out of bounds {config["min_len"]}–{config["max_len"]}'
        )
        raise hug.HTTPBadRequest(
            "seq",
            f"The sequence should be longer that {config['min_len']} and "
            + f"shorter than {config['max_len']}pb",
        )

    matches = searchers["marine"].search(fasta_seq, threshold)
    logging.info(f"Found {len(matches)} matches")

    return {"query": fasta_seq, "threshold": threshold, "results": matches}


@hug.not_found()
def not_found_handler():
    return "Not Found"


@hug.cli()
@hug.local()
def index(
    genomes_dir: hug.types.text,
    index_output: hug.types.text,
    fasta_glob_filter: hug.types.text = "**/*.fna",
    clobber: hug.types.boolean = False,
):
    """
    Builds a COBS index for a folder (catalogue) of genomes.

    :param genomes_dir: Path to a parent folder in which genomes are present. E.g. /path/to/mag_catalogues/marine1.0
    :param index_output: Path to / name of the resulting index. .cobs_compact will be auto-appended.
    :param fasta_glob_filter: Glob filter string to find fasta files within `genomes_dir`. E.g. **.fna
    :param clobber: Set True to enable COBS to clobber/overwrite existing outputs.

    Catalogues will be built as catalogue_name.cobs_compact/
    """
    fasta_list = cobs.DocumentList()

    if not Path(genomes_dir).is_dir():
        raise Exception(f"{genomes_dir} does not appear to be a directory")

    for fasta in Path(genomes_dir).glob(fasta_glob_filter):
        fasta_list.add(str(fasta))

    logging.info(f"Found {len(fasta_list)} FASTA files to index")

    p = cobs.CompactIndexParameters()
    p.clobber = clobber

    cobs.compact_construct_list(fasta_list, index_output + ".cobs_compact", p)
    logging.info(f"Built {index_output}.cobs_compact")


if __name__ == "__main__":
    index.interface.cli()
