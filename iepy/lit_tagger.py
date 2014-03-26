import json
import urllib
import codecs

from iepy.models import PreProcessSteps, Entity, EntityOccurrence
from iepy.ner import NERRunner
from iepy.preprocess import BasePreProcessStepRunner


class OldLitTagger:

    def __init__(self, label, src_filename):
        self.label = label
        self.src_filename = src_filename
        
        f = open(src_filename)
        namelist = f.read().strip().split('\n')
        self.names = frozenset(namelist)
        
        # compute prefix closure
        prefixes = set()
        for name in self.names:
            sname = name.split()
            prefixes.update([' '.join(sname[:i]) for i in range(1, len(sname) + 1)])
        
        self.prefixes = frozenset(prefixes)
    
    def tag(self, sent):
        """Tagger with output a la Stanford (no start/end markers).
        """
        entities = self.entities(sent)
        # dummy entity for nicer code:
        entities.append((len(sent), len(sent)))
        next_entity = entities.pop(0)
        result = []
        for i, t in enumerate(sent):
            #print i, next_entity
            if i >= next_entity[1]:
                # assert entities
                next_entity = entities.pop(0)
            
            if i < next_entity[0]:
                result.append((t, 'O'))
            elif i < next_entity[1]:
                result.append((t, self.label))
        
        return result

    def entities(self, sent):
        """Return entities as a list of pairs (offset, offset_end).
        """
        result = []
        i = 0
        while i < len(sent):
            j = i + 1
            prev_segment = segment = ' '.join(sent[i:j])
            #print 'check: ', segment
            while segment in self.prefixes and j <= len(sent):
                j += 1
                prev_segment = segment
                segment = ' '.join(sent[i:j])
            if prev_segment in self.names:
                result.append((i, j - 1))
                i = j - 1
            else:
                i += 1
        
        return result


class LitTagger:
    
    def __init__(self, labels, src_filenames):
        assert len(labels) == len(src_filenames)
        self.labels = labels
        self.src_filenames = src_filenames
    
        names = set()
        names_map = {}
        for label, filename in zip(labels, src_filenames):
            f = open(filename)
            namelist = f.read().strip().split('\n')
            names.update(namelist)
            for name in namelist:
                names_map[name] = label
        self.names = frozenset(names)
        self.names_map = names_map
        
        # compute prefix closure
        prefixes = set()
        for name in self.names:
            sname = name.split()
            prefixes.update([' '.join(sname[:i]) for i in range(1, len(sname) + 1)])
        
        self.prefixes = frozenset(prefixes)

    def entities(self, sent):
        """Return entities as a list of pairs ((offset, offset_end), label).
        """
        result = []
        i = 0
        while i < len(sent):
            j = i + 1
            prev_segment = segment = ' '.join(sent[i:j])
            #print 'check: ', segment
            while segment in self.prefixes and j <= len(sent):
                j += 1
                prev_segment = segment
                segment = ' '.join(sent[i:j])
            if prev_segment in self.names:
                label = self.names_map[prev_segment]
                result.append(((i, j - 1), label))
                i = j - 1
            else:
                i += 1
        
        return result


class LitTaggerRunner(NERRunner):

    def __init__(self, label, src_filename, override=False):
        lit_tagger = LitTagger(label, src_filename)
        callable_lit_tagger = lambda x: lit_tagger.tag(x)
        NERRunner.__init__(self, callable_lit_tagger, override)


class LitTaggerRunner2(BasePreProcessStepRunner):

    def __init__(self, labels, src_filenames, override=False):
        self.lit_tagger = LitTagger(labels, src_filenames)
    
    def __call__(self, doc):
        # this step does not requires PreProcessSteps.tagging:
        if not doc.was_preprocess_done(PreProcessSteps.sentencer):
            return
        
        entities = []
        sent_offset = 0
        for sent in doc.get_sentences():
            sent_entities = self.lit_tagger.entities(sent)
            
            """for (i, j) in sent_entities:
                name = ' '.join(sent[i:j])
                kind = self.label.lower() # XXX: should be in models.ENTITY_KINDS
                entity, created = Entity.objects.get_or_create(key=name, 
                            defaults={'canonical_form': name, 'kind': kind})
                entity_oc = EntityOccurrence(entity=entity, 
                                        offset=sent_offset + i, 
                                        offset_end=sent_offset + j)
                entities.append(entity_oc)"""
            for ((i, j), label) in sent_entities:
                name = ' '.join(sent[i:j])
                kind = label.lower() # XXX: should be in models.ENTITY_KINDS
                entity, created = Entity.objects.get_or_create(key=name, 
                            defaults={'canonical_form': name, 'kind': kind})
                entity_oc = EntityOccurrence(entity=entity, 
                                        offset=sent_offset + i, 
                                        offset_end=sent_offset + j)
                entities.append(entity_oc)
            
            sent_offset += len(sent)

        doc.set_preprocess_result(PreProcessSteps.nerc, entities)
        doc.save()


def download_freebase_type(type_name, dest_filename, normalizer=None, aliases=False):
    if not normalizer:
        normalizer = lambda x: x
    
    # https://developers.google.com/freebase/v1/mql-overview
    service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
    #query = [{'type': '/medicine/disease', 'name': None}]
    query = [{'type': type_name, 'name': None}]
    if aliases:
        query[0]['/common/topic/alias'] = []
    
    f = codecs.open(dest_filename, 'w', encoding='utf8')

    params = { 'query': json.dumps(query) }
    url = service_url + '?' + urllib.urlencode(params) + '&cursor'
    response = json.loads(urllib.urlopen(url).read())
    cursor = response['cursor']
    
    # write results
    for result in response['result']:
        name = normalizer(result['name'])
        f.write(name + '\n')
        if aliases:
            for name in result['/common/topic/alias']:
                name = normalizer(name)
                f.write(name + '\n')
    
    while cursor:
        params = { 'query': json.dumps(query), 'cursor': cursor }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())
        cursor = response['cursor']
        
        # write results
        for result in response['result']:
            if result['name']:
                name = normalizer(result['name'])
                f.write(name + '\n')
            if aliases:
                for name in result['/common/topic/alias']:
                    name = normalizer(name)
                    f.write(name + '\n')
        
    f.close()

