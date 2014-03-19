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

