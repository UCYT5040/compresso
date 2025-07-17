import click

from . import compress, decompress


@click.group()
def compresso():
    pass


compress_command = click.Command('compress',
                                 callback=compress,
                                 params=[
                                     click.Argument(['filename'], type=click.Path(exists=True)),
                                     click.Option(['--output', '-o'], type=click.Path(), default=None,
                                                  help='Output file for compressed data.'),
                                     click.Option(['--num-threads', '-T'], type=int, default=None,
                                                  help='Number of threads to use for compression.'),
                                     click.Option(['--worker-timeout', '-t'], type=int, default=None,
                                                  help='Timeout for worker threads in seconds.'),
                                     click.Option(['--max-rounds', '-r'], type=int, default=None,
                                                  help='Maximum number of compression rounds to perform.')
                                 ])
decompress_command = click.Command('decompress',
                                   callback=decompress,
                                   params=[
                                       click.Argument(['filename'], type=click.Path(exists=True))
                                   ])
compresso.add_command(compress_command)
compresso.add_command(decompress_command)

if __name__ == '__main__':
    compresso()
