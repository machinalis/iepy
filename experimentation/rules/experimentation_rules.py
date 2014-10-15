# -*- coding: utf-8 -*-

"""
Rules that are going to be used in the experiments
"""

from refo import Question, Star, Any
from iepy.extraction.rules_core import rule, Token


# Examples:
# @rule()
# def always_match(Subject, Object):
#     return Question(Star(Any()))
#
# @rule()
# def match_hello(Subject, Object):
#     return Token("hello")
