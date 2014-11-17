# -*- coding: utf-8 -*-

import os
import wget
import logging
from iepy.utils import DIRS, unzip_file

from nltk.parse import stanford


logger = logging.getLogger(__name__)
stanford_parser_name = 'stanford-parser-full-2014-10-31'
download_url_base = 'http://nlp.stanford.edu/software/'

parser_folder = os.path.join(DIRS.user_data_dir, stanford_parser_name)
os.environ['STANFORD_PARSER'] = parser_folder
os.environ['STANFORD_MODELS'] = parser_folder


class StanfordLexParser:
    def __init__(self):
        if not os.path.exists(parser_folder):
            raise LookupError(
                "Stanford parser not found. Try running the "
                "command download_third_party_data.py"
            )
        self.parser = stanford.StanfordParser()

    def parse_document(self, document):
        try:
            parsed = list(self.parser.parse_sents(document.get_sentences()))
        except OSError:
            # Java command failed
            parsed = []
        return parsed


def download():
    logger.info("Downloading Stanford parser...")
    try:
        raise StanfordLexParser()
    except LookupError:
        # Package not found, lets download and install it
        if not os.path.exists(DIRS.user_data_dir):
            os.mkdir(DIRS.user_data_dir)
        os.chdir(DIRS.user_data_dir)
        package_filename = '{0}.zip'.format(stanford_parser_name)
        zip_path = os.path.join(DIRS.user_data_dir, package_filename)
        wget.download(download_url_base + package_filename)
        unzip_file(zip_path, DIRS.user_data_dir)
    else:
        logger.info("Stanford parser is already downloaded and functional.")
