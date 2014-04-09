"""
Cross-validate IEPY classifier

Usage:
    cross_validate.py [--k=<subsamples>] <dbname> <gold_standard>
    cross_validate.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  --k=<subsamples>      Number of subsamples [default: 10]
"""

import codecs
import csv

from docopt import docopt

from iepy import db
from iepy.core import Knowledge, Fact, Evidence
from iepy.fact_extractor import FactExtractorFactory

config = {
    # Add config options here
}


def load_evidence_from_csv(filename, connection):
    result = Knowledge()
    with codecs.open(filename, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            entity_a = db.get_entity(row[0], row[1])
            entity_b = db.get_entity(row[2], row[3])
            f = Fact(entity_a, row[4], entity_b)
            s = db.get_segment(row[5])
            e = Entity(fact=f, segment=s, o1=int(row[6]), o2=int(row[7]))
            result[e] = float(row[8])
    return result


def main(options):
    connection = db.connect(options['<dbname>'])
    standard = load_evidence_from_csv(options['<gold_standard>'], connection)
    k = int(options['subsamples'])

    success = total = 0
    for subsample in range(k):
        train_data = Knowledge()
        test_data = []
        test_labels = []
        for i, (e, s) in enumerate(standard.items()):
            if i % k == subsample:
                test_data.append(e)
                test_labels.append(s)
            else:
                train_data[e] = s
        extractor = FactExtractorFactory(config, train_data)
        prediction = extractor.predict(test_data)
        assert len(prediction) == len(test_data)
        total += len(prediction)
        success = sum(1 for (p, e) in zip(prediction, test_labels) if p == e)
    return success / total

if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    score = main(opts)
    print("%.3f" % score)

