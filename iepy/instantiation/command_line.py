#!/usr/bin/env python

"""
IEPY instance creator.

Usage:
    iepy --download-third-party-data
    iepy <folder_name>

Options:
  --download-third-party-data       Downloads the necesary data from third party software
  -h --help                         Show this screen
"""

import os
import sys
import json
import errno
import shutil

import nltk.data
from docopt import docopt
from django.utils.crypto import get_random_string

from iepy import defaults
from iepy.utils import DIRS
from iepy.preprocess.tagger import download as download_tagger
from iepy.preprocess.corenlp import download as download_corenlp
from iepy.preprocess.ner.stanford import download as download_ner

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def execute_from_command_line(argv=None):
    opts = docopt(__doc__, argv=argv, version=0.1)
    folder_name = opts["<folder_name>"]

    if opts["--download-third-party-data"]:
        download_third_party_data()
        return

    if os.path.exists(folder_name):
        print("Folder already exists")
        sys.exit(1)

    files_to_copy = [
        os.path.join(THIS_FOLDER, "csv_to_iepy.py"),
        os.path.join(THIS_FOLDER, "preprocess.py"),
        os.path.join(THIS_FOLDER, "iepy_runner.py"),
        os.path.join(THIS_FOLDER, "iepy_rules_runner.py"),
    ]

    # Create folders
    bin_folder = os.path.join(folder_name, "bin")

    os.mkdir(folder_name)
    os.mkdir(bin_folder)

    for filepath in files_to_copy:
        filename = os.path.basename(filepath)
        destination = os.path.join(bin_folder, filename)
        shutil.copyfile(filepath, destination)

    # Create empty rules file
    rules_filepath = os.path.join(folder_name, "rules.py")
    with open(rules_filepath, "w") as filehandler:
        filehandler.write("# Write here your rules\n")
        filehandler.write("# RELATION = 'your relation here'\n")

    # Create extractor config
    extractor_config_filepath = os.path.join(folder_name, "extractor_config.json")
    with open(extractor_config_filepath, "w") as filehandler:
        json.dump(defaults.extractor_config, filehandler, indent=4)

    # Create the settings file
    print("An sqlite database will be created for you to work with.")
    database_name = input("Database name: ")
    settings_filepath = os.path.join(folder_name, "settings.py")
    settings_data = get_settings_string(database_name)
    with open(settings_filepath, "w") as filehandler:
        filehandler.write(settings_data)


def download_third_party_data():
    print("Making sure configuration folder exists")
    try:
        os.makedirs(DIRS.user_data_dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(DIRS.user_data_dir):
            pass
        else:
            raise
    print("Downloading punkt tokenizer")
    nltk.download("punkt")
    print("Downloading wordnet")
    nltk.download("wordnet")
    download_tagger()
    download_ner()
    download_corenlp()


def get_settings_string(database_name):
    template_settings_filepath = os.path.join(THIS_FOLDER, "settings.py.template")
    with open(template_settings_filepath) as filehandler:
        settings_data = filehandler.read()

    if not database_name.endswith(".sqlite"):
        database_name += ".sqlite"

    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(50, chars)
    settings_data = settings_data.replace("{SECRET_KEY}", secret_key)
    settings_data = settings_data.replace("{DATABASE_NAME}", database_name)

    return settings_data


if __name__ == "__main__":
    execute_from_command_line()
