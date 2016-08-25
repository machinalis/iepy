import os
import os.path
import logging

from nltk.tag.stanford import StanfordPOSTagger
import wget

from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps
from iepy.utils import DIRS, unzip_file


logger = logging.getLogger(__name__)
stanford_postagger_name = 'stanford-postagger-2014-01-04'
download_url_base = 'http://nlp.stanford.edu/software/'


class TaggerRunner(BasePreProcessStepRunner):
    """Wrapper to insert a generic callable sentence POS tagger into the pipeline.
    In order to run, require documents with sentence splitting already done.
    """
    step = PreProcessSteps.tagging

    def __init__(self, postagger, override=False):
        """override:
        """
        self.postagger = postagger
        self.override = override

    def __call__(self, doc):
        if not doc.was_preprocess_step_done(PreProcessSteps.sentencer):
            # cannot proceed if the document wasn't split in senteces
            return
        if not self.override and doc.was_preprocess_step_done(PreProcessSteps.tagging):
            return

        tagged_doc = []
        for ts in self.postagger(doc.get_sentences()):
            tagged_doc.extend(tag for token, tag in ts)

        assert len(tagged_doc) == len(doc.tokens)

        doc.set_tagging_result(tagged_doc)
        doc.save()
        logger.debug("POS tagged a document")


class StanfordTaggerRunner(TaggerRunner):

    def __init__(self, override=False):
        tagger_path = os.path.join(DIRS.user_data_dir, stanford_postagger_name)
        if not os.path.exists(tagger_path):
            raise LookupError("Stanford POS tagger not found. Try running the "
                              "command download_third_party_data.py")

        postagger = StanfordPOSTagger(
            os.path.join(tagger_path, 'models', 'english-bidirectional-distsim.tagger'),
            os.path.join(tagger_path, 'stanford-postagger.jar'),
            encoding='utf8')
        super(StanfordTaggerRunner, self).__init__(postagger.tag_sents, override)


def download():
    logger.info("Downloading Stanford POS tagger...")
    try:
        StanfordTaggerRunner()
    except LookupError:
        if not os.path.exists(DIRS.user_data_dir):
            os.mkdir(DIRS.user_data_dir)
        os.chdir(DIRS.user_data_dir)
        package_filename = '{0}.zip'.format(stanford_postagger_name)
        zip_path = os.path.join(DIRS.user_data_dir, package_filename)
        wget.download(download_url_base + package_filename)
        unzip_file(zip_path, DIRS.user_data_dir)
    else:
        logger.info("Stanford POS tagger is already downloaded and functional.")
