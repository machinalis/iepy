"""
IEPY's result pretty printer.

Usage:
    print_results.py <dbname> <csv_file> [options]
    print_results.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  --with-score         Shows colored scores
  --with-line-number    Shows each item numbered sequentially
"""
from docopt import docopt

from colorama import Back, Style

from iepy import db
from iepy.knowledge import Knowledge


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connection = db.connect(opts['<dbname>'])
    csv_file = opts['<csv_file>']
    evidence = Knowledge.load_from_csv(csv_file)

    for nr, (e, score) in enumerate(evidence.items()):
        fact = e.colored_fact()
        fact_line = []
        if opts['--with-line-number']:
            fact_line.append(str(nr+1))
        if opts['--with-score']:
            if score == 0:
                score_color = Back.YELLOW
            elif score == 1:
                score_color = Back.MAGENTA
            else:
                score_color = Back.CYAN
            colored_score = u''.join([score_color, str(score), Style.RESET_ALL])
            fact_line.append(colored_score)
        fact_line.append(u'FACT: {}'.format(fact))
        print(u'\n' + u'\t'.join(fact_line))
        if e.segment:
            text = e.colored_text()
            print(u'  SEGMENT: {}'.format(text))
