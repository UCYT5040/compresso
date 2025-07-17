import bz2

from compresso.algorithms.base import Algorithm
class Bz2Algorithm(Algorithm):
    ID = 3

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        return bz2.compress(data)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        return bz2.decompress(data)
