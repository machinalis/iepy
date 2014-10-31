#!/usr/bin/env python

"""
IEPY administration command.

Usage:
    iepy --create <folder_path>
    iepy --upgrade <folder_path>
    iepy --download-third-party-data

Options:
  --create                          Creates new IEPY instance
  --upgrade                         Upgrades IEPY instance
  --download-third-party-data       Downloads the necesary data from third party software
  -h --help                         Show this screen
  --version                         Version number
"""

import nltk.data
from docopt import docopt


import iepy
from iepy.instantiation.instance_admin import InstanceManager
from iepy.preprocess.tagger import download as download_tagger
from iepy.preprocess.corenlp import download as download_corenlp
from iepy.preprocess.ner.stanford import download as download_ner


def execute_from_command_line(argv=None):
    opts = docopt(__doc__, argv=argv, version=iepy.__version__)
    if opts["--download-third-party-data"]:
        download_third_party_data()
    elif opts["--create"]:
        InstanceManager(opts["<folder_path>"]).create()
    elif opts['--upgrade']:
        InstanceManager(opts["<folder_path>"]).upgrade()


def download_third_party_data():
    print("Downloading punkt tokenizer")
    nltk.download("punkt")
    print("Downloading wordnet")
    nltk.download("wordnet")
    download_tagger()
    download_ner()
    download_corenlp()


if __name__ == "__main__":
    execute_from_command_line()
