from nltk.tag.stanford import POSTagger

from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


stanford_tagger_path = '../stanford-postagger-2014-01-04/'
stanford_ner_path = '../stanford-ner-2014-01-04/'


class StanfordTaggerRunner(BasePreProcessStepRunner):
    """Wrapper to insert a generic callable sentence POS tagger into the pipeline.
    """
    step = PreProcessSteps.tagging
    
    def __init__(self, override=False):
        """override:
        """
        self.override = override
        self.pos_tagger = POSTagger(stanford_tagger_path + 
                                'models/english-bidirectional-distsim.tagger', 
                                stanford_tagger_path + 'stanford-postagger.jar')

    def __call__(self, doc):
        if not doc.was_preprocess_done(PreProcessSteps.segmentation):
            return
        if not self.override and doc.was_preprocess_done(PreProcessSteps.tagging):
            #print 'Already done'
            return
            
        tagged_doc = []
        for sent in doc.get_sentences():
            tagged_sent = self.pos_tagger.tag(sent)
            tagged_doc.extend([tag for token, tag in tagged_sent])
            
        doc.set_preprocess_result(PreProcessSteps.tagging, tagged_doc)
        doc.save()

