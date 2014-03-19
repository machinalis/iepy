import json
import urllib
import codecs


class LitTagger:

    def __init__(self, label, src_filename):
        self.label = label
        self.src_filename = src_filename
        #names = set()
        #for filename in src_filenames:
        #    f = open(filename)
        #    namelist = f.read().strip().split('\n')
        #    names.update(namelist)
        #self.names = frozenset(names)
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
                # label sent[i:j - 1]
                for k in range(i, j - 1):
                    result.append((sent[k], self.label))
                i = j - 1
            else:
                result.append((sent[i], 'O'))
                i += 1
        
        return result


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

