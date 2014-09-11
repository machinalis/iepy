import errno
import os

import nltk.data
from iepy.preprocess.tagger import download as download_tagger
from iepy.preprocess.ner.stanford import download as download_ner
from iepy.utils import DIRS


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


if __name__ == "__main__":
    print("Downloading third party software...")
    download_third_party_data()
    print("Done.")
