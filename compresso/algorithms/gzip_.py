import gzip
from compresso.algorithms.base import Algorithm

class GZipAlgorithm(Algorithm):
    ID = 1

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        return gzip.compress(data)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        return gzip.decompress(data)
