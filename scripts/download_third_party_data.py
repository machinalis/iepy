import nltk.data
from iepy.tagger import download as download_tagger
from iepy.ner import download as download_ner

def download_third_party_data():
    print("Downloading punkt tokenizer")
    nltk.download("punkt", "/tmp")
    download_tagger()
    download_ner()


if __name__ == "__main__":
    print("Downloading third party software...")
    download_third_party_data()
    print("Done.")
