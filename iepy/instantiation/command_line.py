#!/usr/bin/env python

"""
IEPY administration command.

Usage:
    iepy --create <folder_path> [--lang=<lang>]
    iepy --upgrade <folder_path>
    iepy --download-third-party-data [--lang=<lang>]

Options:
  --create                          Creates new IEPY instance
  --upgrade                         Upgrades IEPY instance
  --download-third-party-data       Downloads the necesary data from third party software
  --lang=<lang>                     Language to use (for downloading data, or instance setup) [default: en]
  -h --help                         Show this screen
  --version                         Version number
"""
import sys
import nltk.data
from docopt import docopt


import iepy
from iepy.instantiation.instance_admin import InstanceManager
from iepy.preprocess.tagger import download as download_tagger
from iepy.preprocess.corenlp import download as download_corenlp
from iepy.preprocess.ner.stanford import download as download_ner

_SUPPORTED_LANGS = ['en', 'es', 'de']


def execute_from_command_line(argv=None):
    opts = docopt(__doc__, argv=argv, version=iepy.__version__)
    lang = opts['--lang']
    if lang not in _SUPPORTED_LANGS:
        print("Language '{}' is not between supported ones ({}).".format(
            lang, ', '.join(_SUPPORTED_LANGS)))
        sys.exit()
    if opts["--download-third-party-data"]:
        download_third_party_data(lang)
    elif opts["--create"]:
        InstanceManager(opts["<folder_path>"], lang=lang).create()
    elif opts['--upgrade']:
        InstanceManager(opts["<folder_path>"]).upgrade()


def download_third_party_data(lang):
    print("Downloading punkt tokenizer")
    nltk.download("punkt")
    print("Downloading wordnet")
    nltk.download("wordnet")
    download_tagger()
    download_ner()
    download_corenlp(lang)


if __name__ == "__main__":
    execute_from_command_line()
