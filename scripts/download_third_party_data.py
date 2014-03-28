import os

import nltk.data
from iepy.tagger import download as download_tagger
from iepy.ner import download as download_ner
from iepy.utils import DIRS


def download_third_party_data():
    print("Downloading punkt tokenizer")
    if not os.path.exists(DIRS.user_data_dir):
        os.mkdir(DIRS.user_data_dir)
    nltk.download("punkt", DIRS.user_data_dir)
    download_tagger()
    download_ner()


if __name__ == "__main__":
    print("Downloading third party software...")
    download_third_party_data()
    print("Done.")
