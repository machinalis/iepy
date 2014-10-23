#!/usr/bin/env python

"""
IEPY instance creator.

Usage:
    iepy --download-third-party-data
    iepy <folder_path>

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
from django.core.management import execute_from_command_line as django_command_line

import iepy
from iepy import defaults
from iepy.utils import DIRS
from iepy.preprocess.tagger import download as download_tagger
from iepy.preprocess.corenlp import download as download_corenlp
from iepy.preprocess.ner.stanford import download as download_ner

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def execute_from_command_line(argv=None):
    opts = docopt(__doc__, argv=argv, version=0.1)
    folder_path = opts["<folder_path>"]

    if opts["--download-third-party-data"]:
        download_third_party_data()
        return

    if os.path.exists(folder_path):
        print("Folder already exists")
        sys.exit(1)

    files_to_copy = [
        os.path.join(THIS_FOLDER, "csv_to_iepy.py"),
        os.path.join(THIS_FOLDER, "preprocess.py"),
        os.path.join(THIS_FOLDER, "iepy_runner.py"),
        os.path.join(THIS_FOLDER, "iepy_rules_runner.py"),
        os.path.join(THIS_FOLDER, "manage.py"),
    ]

    # Create folders
    bin_folder = os.path.join(folder_path, "bin")

    os.mkdir(folder_path)
    os.mkdir(bin_folder)

    for filepath in files_to_copy:
        filename = os.path.basename(filepath)
        destination = os.path.join(bin_folder, filename)
        shutil.copyfile(filepath, destination)

    # Create empty rules file
    rules_filepath = os.path.join(folder_path, "rules.py")
    with open(rules_filepath, "w") as filehandler:
        filehandler.write("# Write here your rules\n")
        filehandler.write("# RELATION = 'your relation here'\n")

    # Create extractor config
    extractor_config_filepath = os.path.join(folder_path, "extractor_config.json")
    with open(extractor_config_filepath, "w") as filehandler:
        json.dump(defaults.extractor_config, filehandler, indent=4)

    # Create the settings file
    print("Initializing database")
    folder_name = folder_path.rsplit(os.sep, 1)
    folder_name = folder_name[1] if len(folder_name) > 1 else folder_name[0]
    database_name = input("Database name [{}]: ".format(folder_name))
    if not database_name:
        database_name = folder_name
    new_settings_filepath = "{}_settings.py".format(folder_name)
    settings_filepath = os.path.join(folder_path, new_settings_filepath)
    settings_data = get_settings_string(database_name)
    with open(settings_filepath, "w") as filehandler:
        filehandler.write(settings_data)

    # Setup IEPY with the new instance
    abs_folder_path = os.path.abspath(folder_path)
    os.chdir(abs_folder_path)
    iepy.setup(abs_folder_path)
    django_command_line(["", "migrate"])

    # Setup the database user
    print("\nCreating database user")
    django_command_line(["", "createsuperuser"])

    print("\n IEPY instance ready to use at '{}'".format(abs_folder_path))


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
