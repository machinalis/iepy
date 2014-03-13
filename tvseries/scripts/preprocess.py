"""
Wikia Series Pre Processing

Usage:
    preprocess.py <dbname>

"""
from docopt import docopt
from mwtextextractor import get_body_text

from iepy.db import connect, DocumentManager
from iepy.preprocess import PreProcessPipeline


def media_wiki_to_txt(doc):
    if not doc.text and doc.metadata['raw_text']:
        doc.text = get_body_text(doc.metadata['raw_text'])
        doc.save()

if __name__ == '__main__':
    import logging
    logger = logging.getLogger('iepy')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])
    docs = DocumentManager()
    pipeline = PreProcessPipeline([media_wiki_to_txt], docs)
    pipeline.process_everything()
