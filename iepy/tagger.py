import urllib
import os
import os.path
from nltk.tag.stanford import POSTagger

from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


stanford_postagger_name = 'stanford-postagger-2014-01-04'
download_url_base = 'http://nlp.stanford.edu/software/'


class TaggerRunner(BasePreProcessStepRunner):
    """Wrapper to insert a generic callable sentence POS tagger into the pipeline.
    """
    step = PreProcessSteps.tagging
    
    def __init__(self, postagger, override=False):
        """override:
        """
        self.postagger = postagger
        self.override = override
        
    def __call__(self, doc):
        if not doc.was_preprocess_done(PreProcessSteps.sentencer):
            return
        if not self.override and doc.was_preprocess_done(PreProcessSteps.tagging):
            #print 'Already done'
            return
            
        tagged_doc = []
        for sent in doc.get_sentences():
            #tagged_sent = self.postagger.tag(sent)
            tagged_sent = self.postagger(sent)
            tagged_doc.extend([tag for token, tag in tagged_sent])
            
        doc.set_preprocess_result(PreProcessSteps.tagging, tagged_doc)
        doc.save()


class StanfordTaggerRunner(TaggerRunner):

    def __init__(self, override=False):
        if not os.path.exists(stanford_postagger_name):
            raise LookupError("Stanford POS tagger not found.")
        
        postagger = POSTagger(stanford_postagger_name + 
                            '/models/english-bidirectional-distsim.tagger', 
                            stanford_postagger_name + '/stanford-postagger.jar')
        callable_postagger = lambda x : postagger.tag(x)
        
        TaggerRunner.__init__(self, callable_postagger, override)


def download():
    print 'Downloading Stanford POS tagger...'
    package_filename = '{0}.zip'.format(stanford_postagger_name)
    #print 'Downloaded {0:3}%'.format(blocks * block_size * 100 / total),
    #def hook(blocks, block_size, total):
    #    print 'Downloaded {0:3}%'.format(blocks * block_size * 100 / total),
    urllib.urlretrieve(download_url_base + package_filename, package_filename)
    os.system('unzip {0}'.format(package_filename))

