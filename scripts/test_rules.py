# -*- coding: utf-8 -*-

from iepy.rules import BaseRule, Pos, Token
from refo import Question, Star, Any


class CausesRules(object):
    relation = "CAUSES"


class TestRule(BaseRule, CausesRules):
    regex = Question(Star(Any())) + Token("team") + Question(Star(Any()))
