import urllib2
import os
import os.path
from nltk.tag.stanford import POSTagger

from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


stanford_tagger_name = 'stanford-postagger-2014-01-04'
download_url_base = 'http://nlp.stanford.edu/software/'


class StanfordTaggerRunner(BasePreProcessStepRunner):
    """Wrapper to insert a generic callable sentence POS tagger into the pipeline.
    """
    step = PreProcessSteps.tagging
    
    def __init__(self, override=False):
        """override:
        """
        # check installation:
        if not os.path.exists(stanford_tagger_name):
            print 'Downloading Stanford POS tagger...'
            package_filename = '{0}.zip'.format(stanford_tagger_name)
            download(download_url_base + package_filename, package_filename)
            os.system('unzip {0}'.format(package_filename))
        
        self.override = override
        self.pos_tagger = POSTagger(stanford_tagger_name + 
                                '/models/english-bidirectional-distsim.tagger', 
                                stanford_tagger_name + '/stanford-postagger.jar')

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


def download(url, filename):
    infile = urllib2.urlopen(url)
    meta = infile.info()
    print 'File size: {0} bytes.'.format(int(meta.getheaders("Content-Length")[0]))
    outfile = open(filename, 'w')
    outfile.write(infile.read())
    infile.close()
    outfile.close()

