"""
Wikia TV series preprocessing script

Usage:
    preprocess.py
    preprocess.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
import logging
import re

from docopt import docopt
from mwtextextractor import get_body_text

from iepy.data.db import DocumentManager, EntityManager
from iepy.preprocess.pipeline import PreProcessPipeline
from iepy.preprocess.tokenizer import TokenizeSentencerRunner
from iepy.preprocess.tagger import StanfordTaggerRunner
from iepy.preprocess.combined_ner import NoOverlapCombinedNERRunner
from iepy.preprocess.literal_ner import LiteralNERRunner
from iepy.preprocess.ner import StanfordNERRunner
from iepy.preprocess.segmenter import SyntacticSegmenterRunner


def media_wiki_to_txt(doc):
    if not doc.text and doc.metadata.get('raw_text', ''):
        # After MW strip, titles will not be recognizable. If they don't end
        # with a dot, it will be very hard to split into sentences correctly.
        raw = doc.metadata['raw_text']
        raw = re.subn(r'(=+)(.*)\1', r'\1\2.\1', raw)[0]
        doc.text = get_body_text(raw)
        doc.save()


CUSTOM_ENTITIES = [u'PERSON', u'DISEASE', u'SYMPTOM', u'MEDICAL_TEST']
CUSTOM_ENTITIES_FILES = [u'examples/tvseries/notable_people.txt',
                         u'examples/tvseries/disease.txt',
                         u'examples/tvseries/symptom.txt',
                         u'examples/tvseries/diagnostic_test.txt']


if __name__ == '__main__':
    logger = logging.getLogger(u'preprocess')
    logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO,
                        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    opts = docopt(__doc__, version=0.1)
    docs = DocumentManager()
    EntityManager.ensure_kinds(CUSTOM_ENTITIES)
    pipeline = PreProcessPipeline([
        media_wiki_to_txt,
        TokenizeSentencerRunner(),
        StanfordTaggerRunner(),
        NoOverlapCombinedNERRunner(
            ners=[LiteralNERRunner(CUSTOM_ENTITIES, CUSTOM_ENTITIES_FILES),
                  StanfordNERRunner()]
        ),
        SyntacticSegmenterRunner(),
    ], docs
    )
    pipeline.process_everything()
