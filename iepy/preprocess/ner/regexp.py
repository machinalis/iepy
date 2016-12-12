import re
import codecs

from nltk.text import TokenSearcher as NLTKTokenSearcher

from iepy.preprocess.ner.base import BaseNERRunner


class RegExpNERRunner(BaseNERRunner):

    def __init__(self, label, regexp, override=False):
        super(RegExpNERRunner, self).__init__(override=override)
        self.label = label
        self.regexp = regexp

    def run_ner(self, doc):
        entities = []
        tokens = doc.tokens
        searcher = TokenSearcher(tokens)
        for match in searcher.finditer(self.regexp):
            entity_oc = self.process_match(match)
            if type(entity_oc) == list:
                entities.extend(entity_oc)
            else:
                entities.append(entity_oc)
        return entities

    def process_match(self, match):
        name = ' '.join(match.group())
        kind = self.label
        offset, offset_end = match.span()
        entity_oc = self.build_occurrence(name, kind, name, offset, offset_end)

        return entity_oc


class TokenSearcher(NLTKTokenSearcher):
    """
    From nltk.text.TokenSearcher documentation:

        A class that makes it easier to use regular expressions to search
        over tokenized strings.  The tokenized string is converted to a
        string where tokens are marked with angle brackets -- e.g.,
        ``'<the><window><is><still><open>'``.  The regular expression
        passed to the ``findall()`` method is modified to treat angle
        brackets as non-capturing parentheses, in addition to matching the
        token boundaries; and to have ``'.'`` not match the angle brackets.
    """

    def __init__(self, tokens):
        # replace < and > inside tokens with \< and \>
        _raw = '><'.join(w.replace('<', '\<').replace('>', '\>') for w in tokens)
        # preprend >< instead of < for easier token counting
        self._raw = '><' + _raw + '>'

    def finditer(self, regexp):
        regexp = preprocess_regexp(regexp)

        i = re.finditer(regexp, self._raw)
        while True:
            try:
                m = next(i)
                start, end = m.span()
                # FIXME: do not count from the beggining
                token_start = self._raw[:start].count('><')
                token_end = self._raw[:end].count('><')
                yield MatchObject(m, token_start, token_end)
            except:
                return


class MatchObject:

    def __init__(self, m, token_start, token_end):
        self.m = m
        self.all = m.group()
        self.all_start, self.all_end = m.span()
        self.token_start = token_start
        self.token_end = token_end

    def group(self, *args):
        result = self.m.group(*args)
        if result:
            return result[1:-1].split('><')
        else:
            return None

    def span(self, *args):
        start, end = self.m.span(*args)
        span_start = self.all[:start - self.all_start].count('<')
        span_end = self.all[:end - self.all_start].count('<')

        return (self.token_start + span_start, self.token_start + span_end)


def preprocess_regexp(regexp):
    # preprocess the regular expression
    regexp = re.sub(r'\s', '', regexp)
    # replace < and > only if not double (<< or >>):
    # FIXME: avoid matching \< and \>.
    regexp = re.sub(r'(?<!<)<(?!<)', '(?:<(?:', regexp)
    regexp = re.sub(r'(?<!>)>(?!>)', ')>)', regexp)
    # now, replace << >> with < > resp.
    regexp = re.sub(r'<<', '<', regexp)
    regexp = re.sub(r'>>', '>', regexp)
    # Replace . (if not preceded by \) with [^>]
    regexp = re.sub(r'(?<!\\)\.', '[^>]', regexp)

    return regexp
