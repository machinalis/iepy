# -*- coding: utf-8 -*-
import re

import nltk.data
from nltk.tokenize import RegexpTokenizer

from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps
from iepy.utils import DIRS


class TokenizeSentencerRunner(BasePreProcessStepRunner):
    """Does Tokenization and segmentation togheter over IEDocuments.

    - If override=True, no matter if any of those steps were
    already computed or not, will do and store them on the doc.
    - If override=False, but one of the 2 things is done and the other
    not, will behave completely like in the case of override=True.
    - If override=False and both steps were done on the document, will
    do nothing.
    """
    step = PreProcessSteps.tokenization

    def __init__(self, override=False, increment=False, lang='en'):
        if lang != 'en':
            # We are right now only providing english tokenization
            # and segmentation. But if you need something else, this
            # is a good place to do it.
            raise NotImplemented
        self.lang = lang
        self.override = override
        self.increment = increment
        # we'll be doing 2 PreProcess in one here
        self.tkn_step = PreProcessSteps.tokenization
        self.snt_step = PreProcessSteps.sentencer

    def __call__(self, doc):
        tkn_done = doc.was_preprocess_step_done(self.tkn_step)
        snt_done = doc.was_preprocess_step_done(self.snt_step)
        if self.override or not (tkn_done and snt_done):
            # Ok, let's do it
            result = en_tokenize_and_segment(doc.text)
            doc.set_tokenization_result(
                list(zip(result['spans'], result['tokens'])))
            doc.set_sentencer_result(result['sentences'])
            doc.save()


def en_tokenize_and_segment(text):
    """
    Tokenizes and segments a string `text` interpreted as english text.
    Returns a tuple `(tokens, spans, sentences)` where:
        - tokens is a list of strings corresponding to the tokens in `text`.
        - spans is a list of the starting offsets i in `text` for each token in
          `tokens`.
        - sentences is a list of indexes that represent the start and end
          position of each sentence like this: the i-th sentence starts on
          token `sentences[i]` and ends on token `sentences[i + 1]`.
          There are `len(sentences) - 1` sentences represented in the list.
    """
    tokenizer = _get_tokenizer()

    tokens = []
    spans = []
    sentences = [0]
    for sentence_i, sentence_j, sentence in _split_in_sentences(text):
        if sentence_i == sentence_j:
            continue
        for i, j in tokenizer.span_tokenize(sentence):
            spans.append(sentence_i + i)
            tokens.append(sentence[i:j])
        sentences.append(len(tokens))
    return {'tokens': tokens,
            'spans': spans,
            'sentences': sentences}


def _split_in_sentences(text):
    if not nltk.data.path or nltk.data.path[-1] != DIRS.user_data_dir:
        nltk.data.path.append(DIRS.user_data_dir)
    sentence_splitter = nltk.data.load("tokenizers/punkt/english.pickle")
    for i, j in sentence_splitter.span_tokenize(text):
        yield i, j, text[i:j]


###
### English tokenizer using regular expressions
###


basic_macros = {
    "AN1": "[a-z0-9]",
    "AN2": "[a-z0-9\\._]",
    "AN3": r"[a-z0-9-_\.~!*'();:@&=+$,/?%#\[\]]"
}
macros = {
    "USERNAME": "{AN1}{AN2}*",
    "HOSTNAME": "{AN1}{AN2}*",
    "HOSTNAME2": r"{AN1}{AN2}*\.{AN2}*",
    "HOSTNAME3": r"{AN1}{AN2}*(:[0-9]{{1,5}})?",
    "HOSTNAME4": r"www\.{AN1}{AN2}*\.{AN2}*(:[0-9]{{1,5}})?",
    "SCHEME": "mailto:|((http|https|ftp|ftps|ssh|git|news)://)",
}
macros = {k: "(" + v.format(**basic_macros) + ")"
          for k, v in macros.items()}
macros.update(basic_macros)

# Smiley detection
eyes = ":;8xX>="
noses = [""] + list("-o")
mouths = list("DP/") + ["}}", "{{", "\\[", "\\]", "\\(", "\\)", "\\|"]
smileys = [x + y + z for x in eyes for y in noses for z in mouths]

HEADER = [
    "([01]?[0-9]|2[0-4]):[0-5]?[0-9](:[0-5]?[0-9])?",  # Time of day
    "''|``",                                           # Quotation
    "{USERNAME}@{HOSTNAME2}",                          # Typical email
    "{SCHEME}({USERNAME}@)?{HOSTNAME3}(/{AN3}*)?",     # URI
    "{HOSTNAME4}",                                     # Typical URL
]

FOOTER = [
    "\w+&\w+",                                         # And words
    "\w+",                                             # Normal words
    "|".join(smileys),                                 # Smileys
    "[()/\[\]\\.,;:\-\"'`~?]|\\.\\.\\.",               # Punctuation marks
    "\S+",                                             # Anything else
]


english_contractions = [
    "ain't",
    "aren't",
    "can't",
    "can't've",
    "'cause",
    "could've",
    "couldn't",
    "couldn't've",
    "didn't",
    "doesn't",
    "don't",
    "hadn't",
    "hadn't've",
    "hasn't",
    "haven't",
    "he'd",
    "he'd've",
    "he'll",
    "he'll've",
    "he's",
    "how'd",
    "how'd'y",
    "how'll",
    "how's",
    "I'd",
    "I'd've",
    "I'll",
    "I'll've",
    "I'm",
    "I've",
    "isn't",
    "it'd",
    "it'd've",
    "it'll",
    "it'll've",
    "it's",
    "let's",
    "ma'am",
    "might've",
    "mightn't",
    "mightn't've",
    "must've",
    "mustn't",
    "mustn't've",
    "needn't",
    "o'clock",
    "oughtn't",
    "oughtn't've",
    "shan't",
    "shan't've",
    "she'd",
    "she'd've",
    "she'll",
    "she'll've",
    "she's",
    "should've",
    "shouldn't",
    "shouldn't've",
    "so's",
    "that's",
    "there'd",
    "there's",
    "they'd",
    "they'll",
    "they'll've",
    "they're",
    "they've",
    "to've",
    "wasn't",
    "we'd",
    "we'll",
    "we'll've",
    "we're",
    "we've",
    "weren't",
    "what'll",
    "what'll've",
    "what're",
    "what's",
    "what've",
    "when's",
    "when've",
    "where'd",
    "where's",
    "where've",
    "who'll",
    "who'll've",
    "who's",
    "who've",
    "why's",
    "will've",
    "won't",
    "won't've",
    "would've",
    "wouldn't",
    "wouldn't've",
    "y'all",
    "y'all'd've",
    "y'all're",
    "y'all've",
    "you'd",
    "you'd've",
    "you'll",
    "you'll've",
    "you're",
    "you've"]

en_regex = HEADER + [
    "[01]?[0-9][-/.][0123]?[0-9][-/.][0-9]{{2,4}}",    # Date mm/dd/yyyy
    "|".join(english_contractions),                    # Common contractions
    "'s",                                              # Possesive
    "\w+([_-]\w+)+",                                   # Normal words+compounds
] + FOOTER


def _get_tokenizer(__cache=[]):
    """
    Get a tokenizer for english.
    """
    if not __cache:
        regex = [x.format(**macros) for x in en_regex]
        regex = u"|".join(regex)
        tokenizer = RegexpTokenizer(regex, flags=re.UNICODE |
                                                 re.MULTILINE |
                                                 re.DOTALL | re.I)
        __cache.append(tokenizer)
    return __cache[0]
