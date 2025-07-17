# Compresso File Format Specification

The Compresso file format efficiently stores compressed data. It uses the `.cmpo` extension.

## Structure

The format consists of a header followed by the raw compressed data.

## Header

### Major Version (byte 0)

- **Type**: `uint8`
- **Description**: Major version of the file format (that is, the leftmost number in the version string).
- **Value**: `1`
- **Length**: 1 byte

This field shall be updated in version 255.0.0.

### Compression Algorithms Count (byte 1)

- **Type**: `uint8`
- **Description**: The number of compression algorithms used in the file.
- **Value**: The number of compression algorithms used.
- **Length**: 1 byte

### Compression Algorithms (multiple bytes)

- **Type**: `uint8` (repeated `Compression Algorithms Count` times)
- **Description**: A list of compression algorithms used in the file.
- **Value**: The IDs of the compression algorithms used, in the order they are applied.
- **Length**: Variable length, depending on the number of algorithms.

## Compression Algorithms

### ZStandard

- **ID**: `0`
- **Format author**: Facebook
- **Implementation author**: Facebook, [Gregory Szorc](https://github.com/indygreg)

### gzip

- **ID**: `1`
- **Format author**: TBD
- **Implementation author**: TBD

### brotli

- **ID**: `2`
- **Format author**: TBD
- **Implementation author**: TBD

### bzip2

- **ID**: `3`
- **Format author**: TBD
- **Implementation author**: TBD

### LZMA2

- **ID**: `4`
- **Format author**: TBD
- **Implementation author**: TBD

### Suggestions?

If there is another compression algorithm you would like to see supported, please open an issue or a pull request.
