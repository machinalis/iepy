"""
IEPY's Freebase type instance names downloader (to be used with the Literal NER).

Usage:
    download_freebase_type.py <freebase_type_name> <output_file> [options]
    download_freebase_type.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  --aliases             Include instance aliases
  --to-lower            Convert non acronyms to lowercase
"""
from docopt import docopt

from iepy.literal_ner import download_freebase_type, to_lower_normalizer

if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    freebase_type_name = opts['<freebase_type_name>']
    output_file = opts['<output_file>']
    aliases = opts['--aliases']
    to_lower = opts['--to-lower']

    if to_lower:
        normalizer = to_lower_normalizer
    else:
        normalizer = None
    download_freebase_type(freebase_type_name, output_file, normalizer, aliases)
