"""
Monkey patch BIGSI to avoid the rocksdb dependency installation
"""

class DB:
    pass


class Options:
    def __init___(*args, **kwargs):
        pass
