"""
Monkey patch BIGSI to avoid the rocksdb dependency installation
"""


class DB:
    pass


class CompressionType:
    no_compression = None
    snappy_compression = "snappy"
    zlib_compression = "z"
    bzip2_compression = "bzip2"
    lz4_compression = "lz4"
    lz4hc_compression = "lz4hc"
    xpress_compression = "xpress"
    zstd_compression = "zstd"
    zstdnotfinal_compression = None


class Options:
    def __init___(*args, **kwargs):
        pass
