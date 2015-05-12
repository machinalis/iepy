"""
Corpus preprocessing script

Usage:
    preprocess.py [options]
    preprocess.py --split-in=<num-splits> --run-part=<num-part>
    preprocess.py --increment-ner
    preprocess.py -h | --help | --version

Options:
  -h --help                      Show this screen
  --multiple-cores=<num-cores>   Number of cores (use all to use every processor)
  --increment-ner                Re run NER and Gazetter for every document. If a document lacked any of the previous steps, will be preprocessed entirely.
  --version                      Version number
"""
import logging

from docopt import docopt

import iepy
import multiprocessing
iepy.setup(__file__)
from iepy.data.db import DocumentManager
from iepy.preprocess.stanford_preprocess import StanfordPreprocess
from iepy.preprocess.pipeline import PreProcessPipeline, PreProcessSteps
from iepy.preprocess.segmenter import SyntacticSegmenterRunner


class ParallelDocManager(DocumentManager):

    def mines_of(self, qset, number_of_processors, my_id):
        K = number_of_processors
        N = my_id
        clause = 'id %%%% %s = %s' % (K, N)
        return qset.extra(where=[clause])

def start_preprocess(docs, increment_ner):
    pipeline = PreProcessPipeline([
        StanfordPreprocess(increment_ner),
        SyntacticSegmenterRunner(increment=True)
    ], docs)
    pipeline.process_everything()

if __name__ == '__main__':
    logger = logging.getLogger(u'preprocess')
    logger.setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    opts = docopt(__doc__, version=iepy.__version__)
    increment_ner = opts['--increment-ner']

    dm = ParallelDocManager()
    all_docs = dm.get_documents_lacking_preprocess(
        [PreProcessSteps.segmentation, PreProcessSteps.syntactic_parsing])

    multiple_cores = opts.get('--multiple-cores')
    split_in = opts.get("--split-in")
    run_part = opts.get("--run-part")

    if multiple_cores:
        if multiple_cores == "all":
            multiple_cores = multiprocessing.cpu_count()
        try:
            multiple_cores = int(multiple_cores)
        except ValueError:
            logger.error("Invalid number of cores")
            exit(1)

        for i in range(multiple_cores):
            process = multiprocessing.Process(
                target=start_preprocess, args=(dm.mines_of(all_docs, multiple_cores, i), increment_ner)
            )
            process.start()
    elif split_in:
        try:
            split_in = int(split_in)
            run_part = int(run_part) - 1
        except ValueError:
            logger.error("Invalid split")
            exit(1)

        if run_part < 0 or run_part > split_in:
            logger.error("Parts must be between 1 and {}".format(split_in))
            exit(1)

        docs = dm.mines_of(all_docs, split_in, run_part)
        start_preprocess(docs, increment_ner)
    else:
        start_preprocess(all_docs, increment_ner)
