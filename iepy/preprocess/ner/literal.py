import codecs

from iepy.preprocess.ner.base import BaseNERRunner


class LiteralNER(object):
    """Trivial Named Entity Recognizer that tags exact matches.
    """

    def __init__(self, labels, src_filenames):
        """The i-th label is used to tag the occurrences of the terms in the
        i-th source file. If a term can have several labels, the last one in
        the list is selected.
        """
        assert len(labels) == len(src_filenames)
        self.labels = labels
        self.src_filenames = src_filenames

        names = set()
        names_map = {}
        for label, filename in zip(labels, src_filenames):
            f = codecs.open(filename, encoding="utf8")
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

    def tag(self, sent):
        """Tagger with output a la Stanford (no start/end markers).
        """
        entities = self.entities(sent)
        # dummy entity for nicer code:
        entities.append(((len(sent), len(sent)), 'X'))
        next_entity = entities.pop(0)
        result = []
        for i, t in enumerate(sent):
            if i >= next_entity[0][1]:
                # assert entities
                next_entity = entities.pop(0)

            if i < next_entity[0][0]:
                result.append((t, 'O'))
            elif i < next_entity[0][1]:
                result.append((t, next_entity[1]))

        return result

    def entities(self, sent):
        """Return entities as a list of pairs ((offset, offset_end), label).
        """
        result = []
        i = 0
        while i < len(sent):
            j = i + 1
            prev_segment = segment = ' '.join(sent[i:j])
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


class LiteralNERRunner(BaseNERRunner):

    def __init__(self, labels, src_filenames, override=False):
        super(LiteralNERRunner, self).__init__(override=override)
        self.lit_tagger = LiteralNER(labels, src_filenames)

    def run_ner(self, doc):
        entities = []
        sent_offset = 0
        for sent in doc.get_sentences():
            sent_entities = self.lit_tagger.entities(sent)

            for ((i, j), label) in sent_entities:
                name = ' '.join(sent[i:j])
                kind = label.lower()  # XXX: should be in models.ENTITY_KINDS

                entities.append(
                    self.build_occurrence(
                        key=name,
                        kind_name=kind,
                        alias=name,
                        offset=sent_offset + i,
                        offset_end=sent_offset + j)
                )

            sent_offset += len(sent)
        return entities


def to_lower_normalizer(name):
    """Utility normalizer that converts a name to lowercase unless it is an
    acronym. To be used as parameter of download_freebase_type().
    """
    words = name.split()
    result = []
    for w in words:
        if not w.isupper():
            w = w.lower()
        result.append(w)
    return ' '.join(result)
