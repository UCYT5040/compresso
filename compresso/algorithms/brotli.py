import brotli

from compresso.algorithms.base import Algorithm


class BrotliAlgorithm(Algorithm):
    ID = 2

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        return brotli.compress(data)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        return brotli.decompress(data)
