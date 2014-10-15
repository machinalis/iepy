# -*- coding: utf-8 -*-

from refo import Question, Star, Any
from iepy.extraction.rules_core import rule, Token, Pos


RELATION = "was born"


@rule()
def born_date_in_parenthesis(Subject, Object):
    """
    For cases like: Gary Sykes (Born 13 February 1984) is a British super featherweight boxer.
    """
    anything = Question(Star(Any()))
    return Subject + Pos("-LRB-") + Token("Born") + Object + Pos("-RRB-") + anything


@rule()
def was_born_explicit_mention(Subject, Object):
    """
    For cases like: Shamsher M. Chowdhury was born in 1950.
    """
    return Subject + Token("was born") + Pos("IN") + Object + Question(Pos("."))


@rule()
def just_born(Subject, Object):
    """
    For cases like: Lyle Eugene Hollister, born 6 July 1923 in Sioux Falls, South Dakota, enlisted in the Navy....
    """
    anything = Question(Star(Any()))
    return Subject + Token(", born") + Object + anything
