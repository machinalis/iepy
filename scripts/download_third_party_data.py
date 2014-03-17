import nltk.data


def download_third_party_data():
    print "Downloading punkt tokenizer"
    nltk.download("punkt", "/tmp")


if __name__ == "__main__":
    print "Downloading third party software..."
    download_third_party_data()
    print "Done."
