from .brotli import BrotliAlgorithm
from .bz2_ import Bz2Algorithm
from .gzip_ import GZipAlgorithm
from.lzma_ import LZMAAlgorithm
from.zstd import ZStdAlgorithm

algorithms = [
    GZipAlgorithm,
    Bz2Algorithm,
    LZMAAlgorithm,
    BrotliAlgorithm,
    ZStdAlgorithm
]