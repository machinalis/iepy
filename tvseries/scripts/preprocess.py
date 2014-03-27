"""
Wikia Series Pre Processing

Usage:
    preprocess.py <dbname>

"""
import re

from docopt import docopt
from mwtextextractor import get_body_text

from iepy.db import connect, DocumentManager
from iepy.models import set_custom_entity_kinds
from iepy.preprocess import PreProcessPipeline
from iepy.tokenizer import TokenizeSentencerRunner
from iepy.lit_tagger import LitTaggerRunner
from iepy.tagger import StanfordTaggerRunner
from iepy.ner import StanfordNERRunner
from iepy.segmenter import SyntacticSegmenterRunner


def media_wiki_to_txt(doc):
    if not doc.text and doc.metadata.get('raw_text', ''):
        # After MW strip, titles will not be recognizable. If they dont
        # with a dot, will be very hard to split in sentences correctly.
        raw = doc.metadata['raw_text']
        raw = re.subn(r'(=+)(.*)\1', r'\1\2.\1', raw)[0]
        doc.text = get_body_text(raw)
        doc.save()


MEDIC_ENTITIES = ['DISEASE', 'SYMPTOM', 'MEDICAL_TEST']


class TVSeriesNERRunner(LitTaggerRunner):

    def __init__(self):
        labels = MEDIC_ENTITIES
        filenames = ['tvseries/disease.txt', 'tvseries/symptom.txt',
                     'tvseries/diagnostic_test.txt']
        super(TVSeriesNERRunner, self).__init__(labels, filenames, override=True)


if __name__ == '__main__':
    import logging
    logger = logging.getLogger('iepy')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])
    docs = DocumentManager()
    set_custom_entity_kinds(zip(map(lambda x: x.lower(), MEDIC_ENTITIES),
                                MEDIC_ENTITIES))
    pipeline = PreProcessPipeline([
        media_wiki_to_txt,
        TokenizeSentencerRunner(),
        StanfordTaggerRunner(),
        TVSeriesNERRunner(),
        StanfordNERRunner(),
        SyntacticSegmenterRunner(),
    ], docs
    )
    pipeline.process_everything()
