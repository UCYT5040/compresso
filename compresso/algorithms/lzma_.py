import lzma
from compresso.algorithms.base import Algorithm

class LZMAAlgorithm(Algorithm):
    ID = 4

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        return lzma.compress(data)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        return lzma.decompress(data)
