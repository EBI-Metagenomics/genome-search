import logging
from pathlib import Path

import cobs_index as cobs
import hug


@hug.cli()
@hug.local()
def create(
    genomes_dir: hug.types.text,
    index_output: hug.types.text,
    fasta_glob_filter: hug.types.text = "**/*.fna",
    clobber: hug.types.boolean = False,
    use_cobs_cache: hug.types.boolean = False,
):
    """
    Builds a COBS index for a folder (catalogue) of genomes.

    :param genomes_dir: Path to a parent folder in which genomes are present. E.g. /path/to/mag_catalogues/marine1.0
    :param index_output: Path to / name of the resulting index. .cobs_compact will be auto-appended.
    :param fasta_glob_filter: Glob filter string to find fasta files within `genomes_dir`. E.g. **.fna
    :param clobber: Set True to enable COBS to clobber/overwrite existing outputs.
    :param use_cobs_cache: Set True to use COBS cache. Indexing will be faster, but pollute genomes_dir with new files.

    Catalogues will be built as catalogue_name.cobs_compact/
    """
    if not use_cobs_cache:
        logging.warning("Disabling COBS cache")
        cobs.disable_cache(True)

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
