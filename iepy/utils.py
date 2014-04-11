import codecs
from csv import reader, writer
from getpass import getuser
import zipfile

from appdirs import AppDirs


DIRS = AppDirs('iepy', getuser())


def unzip(zipped_list, n):
    """returns n lists with the elems of zipped_list unsplitted.
    The general case could be solved with zip(*zipped_list), but here we
    are dealing with:
      - un-zipping empy list to n empty lists
      - ensuring that all zipped items in zipped_list have lenght n, raising
        ValueError if not.
    """
    if not zipped_list:
        return tuple([[]]*n)
    else:
        if not all(isinstance(x, tuple) and len(x) == n for x in zipped_list):
            raise ValueError
        return zip(*zipped_list)


def unzip_file(zip_path, extraction_base_path):
    zfile = zipfile.ZipFile(zip_path)
    zfile.extractall(extraction_base_path)


def load_facts_from_csv(filepath):
    """Returns an iterable of facts from a CSV file encoded in UTF-8.
    It's assumend that first 4 columns are
        entity a kind, entity a key, entity b kind, entity b key
    and that the 5th column is the relation name.
    Everything else in the file will be ignored.
    Row with less column than stated, will be ignored.
    """
    from iepy.core import Fact  # Done here to avoid circular dependency
    from iepy import db


    with codecs.open(filepath, mode='r', encoding='utf-8') as csvfile:
        factsreader = reader(csvfile, delimiter=',')
        for row in factsreader:
            if len(row) < 5:
                continue
            entity_a = db.get_entity(row[0], row[1])
            entity_b = db.get_entity(row[2], row[3])
            yield Fact(entity_a, row[4], entity_b)


def save_facts_to_csv(facts, filepath):
    """Writes an iterable of facts to a CSV file encoded in UTF-8.
    Each fact in the input facts iterable is a 3-uple
        entity a, entity b, relation name
    The entities can be Entity or EntityInSegment instances. The relation name
    is a string.
    For the CSV file format refer to load_facts_from_csv().
    """
    with codecs.open(filepath, mode='w', encoding='utf-8') as csvfile:
        facts_writer = writer(csvfile, delimiter=',')
        for (entity_a, entity_b, relation) in facts:
            row = [entity_a.kind, entity_a.key, entity_b.kind, entity_b.key,
                    relation]
            facts_writer.writerow(row)


def save_labeled_evidence_to_csv(labeled_evidence, filepath):
    """Writes an iterable of labeled evidence to a CSV file encoded in UTF-8.
    Each labeled evidence is a 4-uple
        text_segment, entity a, entity b, relation name, label
    The entities are EntityInSegment instances in text_segment.entities.
    The relation name is a string. The label is a boolean.
    The output CSV format is
        entity a kind, entity a key, entity b kind, entity b key,
        relation name, document name, segment offset, 
        entity a index, entity b index, label
    """
    with codecs.open(filepath, mode='w', encoding='utf-8') as csvfile:
        evidence_writer = writer(csvfile, delimiter=',')
        for (segment, entity_a, entity_b, relation, label) in labeled_evidence:
            entity_a_index = segment.entities.index(entity_a)
            entity_b_index = segment.entities.index(entity_b)
            row = [entity_a.kind, entity_a.key, entity_b.kind, entity_b.key,
                    relation, segment.document.human_identifier, segment.offset,
                    entity_a_index, entity_b_index, label]
            evidence_writer.writerow(row)

