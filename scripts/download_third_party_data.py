import nltk.data
from iepy.tagger import download as download_tagger


def download_third_party_data():
    print "Downloading punkt tokenizer"
    nltk.download("punkt", "/tmp")
    download_tagger()


if __name__ == "__main__":
    print "Downloading third party software..."
    download_third_party_data()
    print "Done."
