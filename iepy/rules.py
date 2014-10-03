# -*- coding: utf-8 -*-

import refo

_EOL = None


class BaseRule(object):
    regex = None
    relation = None

    def match(self, rich_tokens):
        match = False
        if self.regex:
            match = refo.match(self.regex + [_EOL], rich_tokens + [_EOL])
        return match


class ObjectAttrPredicate(refo.Predicate):
    def __init__(self, attr_name, attr_value):
        self.attr_name = attr_name
        self.attr_value = attr_value
        super().__init__(self._predicate)
        self.arg = attr_value

    def _predicate(self, obj):
        return obj != _EOL and getattr(obj, self.attr_name) == self.attr_value


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


def Pos(string):
    return obj_attr_predicate_factory(string, "pos")
