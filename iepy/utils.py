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
        return tuple([[]] * n)
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


def load_evidence_from_csv(filename, connection):
    # Importing here to avoid circular dependency
    from iepy.core import Evidence, Fact, Knowledge
    from iepy import db
    result = Knowledge()
    with codecs.open(filename, encoding='utf-8') as csvfile:
        csv_reader = reader(csvfile)
        for row in csv_reader:
            entity_a = db.get_entity(row[0], row[1])
            entity_b = db.get_entity(row[2], row[3])
            f = Fact(entity_a, row[4], entity_b)
            if row[5]:
                s = db.get_segment(row[5], int(row[6]))
                e = Evidence(fact=f, segment=s, o1=int(row[7]), o2=int(row[8]))
                assert s.entities[e.o1].key == entity_a.key
                assert s.entities[e.o2].key == entity_b.key
            else:
                # fact with no evidence
                e = Evidence(fact=f, segment=None, o1=None, o2=None)
            result[e] = int(row[9] == "True")
    return result


def save_facts_to_csv(facts, filepath):
    """Writes an iterable of facts to a CSV file encoded in UTF-8.
    Each fact in the input facts iterable is a Fact instance
    The entities can be Entity or EntityInSegment instances. The relation name
    is a string.
    For the CSV file format refer to load_facts_from_csv().
    """
    with codecs.open(filepath, mode='w', encoding='utf-8') as csvfile:
        facts_writer = writer(csvfile, delimiter=',')
        for (entity_a, relation, entity_b) in facts:
            row = [entity_a.kind, entity_a.key, entity_b.kind, entity_b.key,
                   relation]
            facts_writer.writerow(row)


def save_labeled_evidence_to_csv(labeled_evidence, filepath):
    """Writes an iterable of labeled evidence to a CSV file encoded in UTF-8.
    Each labeled evidence is a 2-uple (evidence, label)
    The entities are EntityInSegment instances in text_segment.entities.
    The relation name is a string. The label is a boolean.
    The output CSV format is
        entity a kind, entity a key, entity b kind, entity b key,
        relation name, document name, segment offset,
        entity a index, entity b index, label
    """
    with codecs.open(filepath, mode='w', encoding='utf-8') as csvfile:
        evidence_writer = writer(csvfile, delimiter=',')
        for (evidence, label) in labeled_evidence:
            entity_a = evidence.fact.e1
            entity_b = evidence.fact.e2
            row = [
                entity_a.kind, entity_a.key,
                entity_b.kind, entity_b.key,
                evidence.fact.relation,
                evidence.segment.document.human_identifier if evidence.segment else "",
                evidence.segment.offset if evidence.segment else "",
                evidence.o1, evidence.o2,
                label
            ]
            evidence_writer.writerow(row)


def make_feature_list(text):
    return [x.strip() for x in text.split("\n") if x.strip()]


def evaluate(predicted_knowledge, gold_knowledge):
    """Computes evaluation metrics for a predicted knowledge with respect to a 
    gold (or reference) knowledge. Returns a dictionary with the results.
    """
    # ignore predicted facts with no evidence:
    predicted_positives = set([p for p in predicted_knowledge.keys() if p.segment])
    gold_positives = set([p for p, b in gold_knowledge.items() if b])
    correct_positives = predicted_positives & gold_positives

    result = {}
    result['correct'] = correct = len(correct_positives)
    result['predicted'] = predicted = len(predicted_positives)
    result['gold'] = gold = len(gold_positives)

    if predicted > 0:
        result['precision'] = precision = float(correct) / predicted
    else:
        result['precision'] = precision = 1.0
    if gold > 0:
        result['recall'] = recall = float(correct) / gold
    else:
        result['recall'] = recall = 1.0
    result['f1'] = 2 * precision * recall / (precision + recall)

    return result
