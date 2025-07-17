class Algorithm:
    ID: int = 0

    @staticmethod
    def compress(self, data: bytes) -> bytes:
        """
        Compress the given data.

        :param data: The data to compress.
        :return: The compressed data.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")

    @staticmethod
    def decompress(self, data: bytes) -> bytes:
        """
        Decompress the given data.

        :param data: The data to decompress.
        :return: The decompressed data.
        """
        raise NotImplementedError("This method should be overridden by subclasses.")
