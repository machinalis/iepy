import itertools
import os
import os.path
import logging

from nltk.tag.stanford import StanfordNERTagger
import wget

from iepy.preprocess.ner.base import BaseNERRunner
from iepy.utils import DIRS, unzip_file

logger = logging.getLogger(__name__)
stanford_ner_name = 'stanford-ner-2014-01-04'
download_url_base = 'http://nlp.stanford.edu/software/'


class NonTokenizingNERTagger(StanfordNERTagger):

    @property
    def _cmd(self):
        old = super(NonTokenizingNERTagger, self)._cmd
        old = old + ["-tokenizerFactory", "edu.stanford.nlp.process.WhitespaceTokenizer"]
        return old


class NERRunner(BaseNERRunner):
    """Wrapper to insert a generic callable sentence NER tagger into the pipeline.
    """
    def __init__(self, ner, override=False):
        super(NERRunner, self).__init__(override=override)
        self.ner = ner

    def run_ner(self, doc):
        entities = []
        # Apply the ner algorithm which takes a list of sentences and returns
        # a list of sentences, each being a list of NER-tokens, each of which is
        # a pairs (tokenstring, class)
        ner_sentences = self.ner(doc.get_sentences())
        # Flatten the nested list above into just a list of kinds
        ner_kinds = (k for s in ner_sentences for (_, k) in s)

        # We build a large iterator z that goes over tuples like the following:
        #  (offset, (token, kind))
        # offset just goes incrementally from 0

        z = itertools.chain(
            enumerate(zip(doc.tokens, ner_kinds)),
            # Add a sentinel last token to simplify last iteration of loop below
            [(len(doc.tokens), (None, 'INVALID'))]
        )

        # Traverse z, looking for changes in the kind field. If there is a
        # change of kind, we have a new set of contiguous tokens; if the kind
        # of those isn't "O" (which means "other"), record the occurrence
        #
        # offset keeps the start of the current token run; last_kind keeps the kind.
        last_kind = 'O'
        offset = 0
        for i, (token, kind) in z:
            if kind != last_kind:
                if last_kind != 'O':
                    # Found a new entity in offset:i
                    name = ' '.join(doc.tokens[offset:i])
                    entities.append(
                        self.build_occurrence(name, last_kind.lower(), name, offset, i)
                    )
                # Restart offset counter at each change of entity type
                offset = i
            last_kind = kind

        # Just a sanity check: verify that all NER tokens were consumed
        try:
            next(ner_kinds)
            assert False, "ner_kinds should have been completely consumed"
        except StopIteration:
            # Actually the stop iteration is the expected result here
            pass

        return entities


class StanfordNERRunner(NERRunner):

    def __init__(self, override=False):
        ner_path = os.path.join(DIRS.user_data_dir, stanford_ner_name)
        if not os.path.exists(ner_path):
            raise LookupError("Stanford NER not found. Try running the "
                              "command download_third_party_data.py")

        ner = NonTokenizingNERTagger(
            os.path.join(ner_path, 'classifiers', 'english.all.3class.distsim.crf.ser.gz'),
            os.path.join(ner_path, 'stanford-ner.jar'),
            encoding='utf8')

        super(StanfordNERRunner, self).__init__(ner.tag_sents, override)


def download():
    logger.info("Downloading Stanford NER...")
    try:
        StanfordNERRunner()
    except LookupError:
        # Package not found, lets download and install it
        if not os.path.exists(DIRS.user_data_dir):
            os.mkdir(DIRS.user_data_dir)
        os.chdir(DIRS.user_data_dir)
        package_filename = '{0}.zip'.format(stanford_ner_name)
        zip_path = os.path.join(DIRS.user_data_dir, package_filename)
        wget.download(download_url_base + package_filename)
        unzip_file(zip_path, DIRS.user_data_dir)
    else:
        logger.info("Stanford NER is already downloaded and functional.")
