# -*- coding: utf-8 -*-

from functools import lru_cache
from collections import namedtuple

import refo

import iepy

TokenToMatch = namedtuple("TokenToMatch", "token lemma pos kinds, is_subj is_obj")


def rule(answer, priority=0):
    if answer not in [False, True]:
        message = "Rule has invalid answer, it has to be either False or True"
        raise ValueError(message)

    def inner(f):
        f.priority = priority
        f.is_rule = True
        f.answer = answer
        return f
    return inner


def is_rule(fun):
    """ Returns whether something is a rule or not """
    is_callable = hasattr(fun, '__call__')
    return is_callable and hasattr(fun, "is_rule") and fun.is_rule


def load_rules():
    result = []
    for attr_name in dir(iepy.instance.rules):
        attr = getattr(iepy.instance.rules, attr_name)
        if is_rule(attr):
            result.append(attr)
    return result


class ObjectAttrPredicate(refo.Predicate):
    def __init__(self, attr_name, attr_value):
        self.attr_name = attr_name
        self.attr_value = attr_value
        super().__init__(self._predicate)
        self.arg = attr_value

    def _predicate(self, obj):
        return getattr(obj, self.attr_name) == self.attr_value


def obj_attr_predicate_factory(attr_values, attr_name):
    attr_values = attr_values.split()
    result = None
    for attr_value in attr_values:
        if result is None:
            result = ObjectAttrPredicate(attr_name, attr_value)
        else:
            result += ObjectAttrPredicate(attr_name, attr_value)
    return result


def Token(string):
    return obj_attr_predicate_factory(string, "token")


def Lemma(string):
    return obj_attr_predicate_factory(string, "lemma")


def Pos(string):
    return obj_attr_predicate_factory(string, "pos")


class Kind(refo.Predicate):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(self._predicate)
        self.arg = kind

    def _predicate(self, obj):
        if hasattr(obj, "kinds"):
            return self.kind in obj.kinds
        return False


class ConditionPredicate(refo.Predicate):
    def __init__(self, **kwargs):
        self.conditions = kwargs
        super().__init__(self._predicate)
        self.arg = str(kwargs)

    def _predicate(self, obj):
        for attr_name, attr_value in self.conditions.items():
            check_inclusion = False
            if attr_name.endswith("__has"):
                attr_name = attr_name[:-5]
                check_inclusion = True

            if hasattr(obj, attr_name):
                if check_inclusion:
                    if not attr_value in getattr(obj, attr_name):
                        return False
                else:
                    if not getattr(obj, attr_name) == attr_value:
                        return False
            else:
                return False
        return True


@lru_cache(maxsize=None)
def compile_rule(rule, relation):
    s, o = generate_subject_and_object(relation)
    return rule(s, o)


@lru_cache(maxsize=8)
def generate_subject_and_object(relation):
    subject_kind = relation.left_entity_kind.name
    object_kind = relation.right_entity_kind.name
    Subject = refo.Plus(ConditionPredicate(is_subj=True, kinds__has=subject_kind))
    Object = refo.Plus(ConditionPredicate(is_obj=True, kinds__has=object_kind))
    return Subject, Object


@lru_cache(maxsize=8)
def cached_segment_enriched_tokens(segment):
    return list(segment.get_enriched_tokens())


@lru_cache(maxsize=8)
def generate_tokens_to_match(evidence):
    tokens_to_match = []
    l_eo_id = evidence.left_entity_occurrence_id
    r_eo_id = evidence.right_entity_occurrence_id

    segment = evidence.segment

    for rich_token in cached_segment_enriched_tokens(segment):
        is_subj = False
        is_obj = False
        if l_eo_id in rich_token.eo_ids:
            is_subj = True
        if r_eo_id in rich_token.eo_ids:
            is_obj = True

        tokens_to_match.append(TokenToMatch(
            token=rich_token.token,
            pos=rich_token.pos,
            lemma=rich_token.lemma,
            kinds=set([x.name for x in rich_token.eo_kinds]),
            is_subj=is_subj,
            is_obj=is_obj,
        ))

    return tokens_to_match
