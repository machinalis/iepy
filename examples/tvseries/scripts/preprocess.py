"""
Wikia TV series preprocessing script

Usage:
    preprocess.py <dbname>
    preprocess.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
import re

from docopt import docopt
from mwtextextractor import get_body_text

from iepy.db import connect, DocumentManager
from iepy.models import set_custom_entity_kinds
from iepy.preprocess import PreProcessPipeline
from iepy.tokenizer import TokenizeSentencerRunner
from iepy.tagger import StanfordTaggerRunner
from iepy.combined_ner import CombinedNERRunner
from iepy.literal_ner import LiteralNERRunner
from iepy.ner import StanfordNERRunner
from iepy.segmenter import SyntacticSegmenterRunner


def media_wiki_to_txt(doc):
    if not doc.text and doc.metadata.get('raw_text', ''):
        # After MW strip, titles will not be recognizable. If they don't end
        # with a dot, it will be very hard to split into sentences correctly.
        raw = doc.metadata['raw_text']
        raw = re.subn(r'(=+)(.*)\1', r'\1\2.\1', raw)[0]
        doc.text = get_body_text(raw)
        doc.save()


CUSTOM_ENTITIES = ['DISEASE', 'SYMPTOM', 'MEDICAL_TEST']
CUSTOM_ENTITIES_FILES = ['examples/tvseries/disease.txt',
                            'examples/tvseries/symptom.txt',
                            'examples/tvseries/diagnostic_test.txt']


if __name__ == '__main__':
    import logging
    logger = logging.getLogger('iepy')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])
    docs = DocumentManager()
    set_custom_entity_kinds(zip(map(lambda x: x.lower(), CUSTOM_ENTITIES),
                                CUSTOM_ENTITIES))
    pipeline = PreProcessPipeline([
        media_wiki_to_txt,
        TokenizeSentencerRunner(),
        StanfordTaggerRunner(),
        CombinedNERRunner(
            LiteralNERRunner(CUSTOM_ENTITIES, CUSTOM_ENTITIES_FILES),
            StanfordNERRunner()),
        SyntacticSegmenterRunner(),
    ], docs
    )
    pipeline.process_everything()
