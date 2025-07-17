# Compresso

Python program that compresses and decompresses files using various algorithms.

See the [SPEC.md](SPEC.md) file for details on the file format.

## Usage

```shell
pip install uv
uv run --module compresso <command> <options> <args>
```

### `compresso compress <file>`

Compress a file using the Compresso format.

#### Options

- `--output <file>` (`-o`): Specify an output file.
- `--num-threads <n>`: Number of threads to use for compression (default: depends on CPU)
- `--worker-timeout <n>`: Timeout in seconds for each worker (default: no timeout).
- `--max-rounds <n>`: Maximum number of rounds to perform (default: unlimited).

## Speed

Compresso can be slow for large files.

Consider adding setting the number threads (`--num_threads <n>`) to speed up compression.

You can also set a timeout in secounds using `--worker-timeout <n>` to limit the time spent on compression. This will
effect compression ratio.

## Effectiveness

On my machine I got the following results with 4 threads and a timeout of 500 seconds:

- `nature.jpg`: 2.83% reduction
- `bbb_sunflower_2160p_30fps_normal.mp4`: 0.11% reduction
- `pg10.txt`: 77.54% reduction

Low reduction amounts could be attributed to the fact that these files are already compressed.

## Test Asset Licenses

Assets used for testing are licensed as follows:

- `nature.jpg`: Free from [Icons8](https://icons8.com/photos/). Please obtain copies from Icons8 for use other than
  testing.
- `bbb_sunflower_2160p_30fps_normal.mp4`: Blender
  Foundation, [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
- `pg10.txt`: Project Gutenberg, [Public Domain](https://www.gutenberg.org/ebooks/10).
