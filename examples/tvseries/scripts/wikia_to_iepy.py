"""
Wikia to IEPy Corpus Builder

Usage:
    wikia_to_iepy.py <wikia_zipped_xml_dump_file> <dbname> <nr_of_seasons> [options]
    wikia_to_iepy.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  --all-episodes-tag=<all-tag>    Wikia tag/category for all episodes [default: Episodes]
  --season-tag-pattern=<season-pattern>  Wikia tag pattern for season episodes [default: Season %i]
"""
from gzip import GzipFile
import logging

from docopt import docopt

import xmltodict

from iepy.db import connect, DocumentManager

logger = logging.getLogger(__name__)


def build_pages_dict(dump_path):
    SerieData = xmltodict.parse(GzipFile(dump_path))
    pages = SerieData['mediawiki']['page']
    return dict([(p['title'], p) for p in pages])


def has_category_tag(page, tag):
    cat_tag = '[[Category:%s]]' % tag
    return cat_tag in page['revision']['text'].get('#text', '')


def get_episode(pages_dict, number_of_seasons, all_tag, season_tag_pattern):
    candidates = [pa for pa in pages_dict.values() if has_category_tag(pa, all_tag)]
    per_season = []
    for i in range(1, number_of_seasons + 1):
        season_tag = season_tag_pattern % i
        season_ep = [pa for pa in candidates if has_category_tag(pa, season_tag)]
        per_season.append(season_ep)
    return per_season

if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])
    docs = DocumentManager()
    pages_dict = build_pages_dict(opts['<wikia_zipped_xml_dump_file>'])
    eps = get_episode(pages_dict, int(opts['<nr_of_seasons>']),
                      opts['--all-episodes-tag'],
                      opts['--season-tag-pattern'])
    for season_nr, season in enumerate(eps, 1):
        for i, e in enumerate(season):
            docs.create_document(
                identifier=e['title'],
                text='',
                metadata={
                    'raw_text': e['revision']['text']['#text'],
                    'season': season_nr,
                    'source': opts['<wikia_zipped_xml_dump_file>']
                })
        logger.info('Dumped %i episodes from season %i', len(season), season_nr)
