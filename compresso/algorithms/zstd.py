import zstandard as zstd

from compresso.algorithms.base import Algorithm


class ZStdAlgorithm(Algorithm):
    ID = 0

    @staticmethod
    def compress(data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        cctx = zstd.ZstdCompressor()
        return cctx.compress(data)

    @staticmethod
    def decompress(data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        dctx = zstd.ZstdDecompressor()
        return dctx.decompress(data)
