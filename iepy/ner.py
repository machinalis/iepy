from nltk.tag.stanford import NERTagger

from iepy.models import PreProcessSteps, Entity, EntityOccurrence
from iepy.preprocess import BasePreProcessStepRunner
from iepy.utils import DIRS, unzip_file

stanford_ner_name = 'stanford-ner-2014-01-04'
download_url_base = 'http://nlp.stanford.edu/software/'


class NERRunner(BasePreProcessStepRunner):
    """Wrapper to insert a generic callable sentence NER tagger into the pipeline.
    """
    # TODO: rename to ner
    step = PreProcessSteps.nerc
    
    def __init__(self, ner, override=False):
        self.ner = ner
        self.override = override
    
    def __call__(self, doc):
        # this step not necessarily requires PreProcessSteps.tagging:
        if not doc.was_preprocess_done(PreProcessSteps.sentencer):
            return
        if not self.override and doc.was_preprocess_done(PreProcessSteps.nerc):
            #print 'Already done'
            return

        entities = []
        sent_offset = 0
        for sent in doc.get_sentences():
            ner_sent = self.ner(sent)
            
            i = 0
            while i < len(ner_sent):
                t, e = ner_sent[i]
                if e != 'O':
                    # entity occurrence found at position i
                    offset = i
                    # find end:
                    i += 1
                    while ner_sent[i][1] == e:
                        i += 1
                    offset_end = i
                    name = ' '.join(sent[offset:offset_end])
                    kind = e.lower() # XXX: should be in models.ENTITY_KINDS
                    entity = Entity(key=name, canonical_form=name, kind=kind)
                    entity.save()
                    entity_oc = EntityOccurrence(entity=entity, 
                                            offset=sent_offset + offset, 
                                            offset_end=sent_offset + offset_end)
                    entities.append(entity_oc)
                else:
                    i += 1
            
            sent_offset += len(sent)
            
        doc.set_preprocess_result(PreProcessSteps.nerc, entities)
        doc.save()

