# -*- coding: utf-8 -*-

from refo import Question, Star, Any, Plus
from iepy.extraction.rules_core import rule, Token, Pos


RELATION = "was born"


@rule(True)
def born_date_in_parenthesis(Subject, Object):
    """
    Ex: Gary Sykes (Born 13 February 1984) is a British super featherweight boxer.
    """
    anything = Star(Any())
    born = Star(Pos(":")) + Question(Token("Born") | Token("born")) + Question(Token("c."))
    entity_leftover = Star(Pos("NNP"))
    return Subject + entity_leftover + Pos("-LRB-") + born + Object + Pos("-RRB-") + anything


@rule(True)
def born_two_dates_in_parenthesis(Subject, Object):
    """
    Ex: James Cunningham (born 1973 or 1974) is a Canadian stand-up comedian and TV host.
    """
    anything = Star(Any())
    born = Question(Token("Born") | Token("born"))
    entity_leftover = Star(Pos("NNP"))
    subject = Subject + entity_leftover
    or_object = (Object + Token("or") + Pos("CD") |
                 Pos("CD") + Token("or") + Object)
    return subject + Pos("-LRB-") + born + or_object + Pos("-RRB-") + anything


@rule(True)
def born_date_and_death_in_parenthesis(Subject, Object):
    """
    Ex: Carl Bridgewater (January 2, 1965 - September 19, 1978) was shot dead
    """
    anything = Star(Any())
    return Subject + Pos("-LRB-") + Object + Token("-") + anything + Pos("-RRB-") + anything


@rule(True)
def born_date_and_place_in_parenthesis(Subject, Object):
    """
    Ex: Gary Sykes (Born 13 February 1984) is a British super featherweight boxer.
    """
    anything = Star(Any())
    born = (Token("Born") | Token("born"))
    entity_leftover = Star(Pos("NNP"))
    place = Plus(Pos("NNP") + Question(Token(",")))
    return Subject + entity_leftover + Pos("-LRB-") + born + Object + Token(",") + place + Pos("-RRB-") + anything


@rule(True)
def was_born_explicit_mention(Subject, Object):
    """
    Ex: Shamsher M. Chowdhury was born in 1950.
    """
    anything = Star(Any())
    return anything + Subject + Token("was born") + Pos("IN") + Object + anything


@rule(True)
def is_born_in(Subject, Object):
    """
    Ex: Xu is born in 1902 or 1903 in a family of farmers in Hubei LRB-- China RRB-- .
    """
    anything = Star(Any())
    return Subject + Token("is born in") + Object + anything


@rule(True)
def mentions_real_name(Subject, Object):
    """
    Ex: Harry Pilling, born Ashtonunder-Lyne, Lancashire on 2 February 1943, played ...
    """
    anything = Star(Any())
    real_name = Plus(Pos("NNP") + Question(Token(",")))
    return Subject + Token("born") + real_name + Pos("IN") + Object + anything


@rule(True)
def was_born_and_mentions_place(Subject, Object):
    """
    Ex: Nasser Sharify was born in Tehran, Iran, in 1925.
    """
    place = Plus(Pos("NNP") + Question(Token(",")))
    return Subject + Token("was born") + Pos("IN") + place + Pos("IN") + Object + Question(Pos("."))


@rule(True)
def was_born_and_mentions_place_2(Subject, Object):
    """
    Ex: Theodone C. Hu was born in 1872 in Huangpu town, Haizhu District, Guangzhou, Guangdong, China.
    """
    anything = Star(Any())
    place = Plus(Pos("NNP") + Question(Token(",")))
    return Subject + Token("was born") + Pos("IN") + Object + Pos("IN") + place + anything


@rule(True)
def just_born(Subject, Object):
    """
    Ex: Lyle Eugene Hollister, born 6 July 1923 in Sioux Falls, South Dakota, enlisted in the Navy....
    """
    anything = Star(Any())
    return Subject + Token(", born") + Object + anything


## NEGATIVE RULES ##

@rule(False, priority=1)
def incorrect_labeling_of_place_as_person(Subject, Object):
    """
    Ex:  Sophie Christiane of Wolfstein (24 October 24, 1667 -- 23 August 1737)
    Wolfstein is a *place*, not a *person*
    """
    anything = Star(Any())
    person = Plus(Pos("NNP") + Question(Token(",")))
    return anything + person + Token("of") + Subject + anything
