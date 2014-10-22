"""
Birthdate corpus preprocessing script

Usage:
    preprocess.py
    preprocess.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
import logging

from docopt import docopt

from iepy.data.db import DocumentManager
from iepy.preprocess.stanford_preprocess import StanfordPreprocess
from iepy.preprocess.pipeline import PreProcessPipeline
from iepy.preprocess.segmenter import SyntacticSegmenterRunner


if __name__ == '__main__':
    logger = logging.getLogger(u'preprocess')
    logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO,
                        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    opts = docopt(__doc__, version=0.1)
    docs = DocumentManager()
    pipeline = PreProcessPipeline([
        StanfordPreprocess(),
        SyntacticSegmenterRunner(increment=True)
    ], docs
    )
    pipeline.process_everything()
