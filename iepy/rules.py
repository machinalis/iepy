# -*- coding: utf-8 -*-

import refo

_EOL = None


class BaseRule(object):
    regex = None
    relation = None

    def match(self, rich_tokens):
        match = False
        if self.regex:
            match = refo.match(
                self.regex + refo.Literal(_EOL),
                rich_tokens + [_EOL]
            )
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


class Kind(refo.Predicate):
    def __init__(self, kind):
        self.kind = kind
        super().__init__(self._predicate)
        self.arg = kind

    def _predicate(self, obj):
        if hasattr(obj, "eo_kinds"):
            obj_kind_names = [x.name for x in obj.eo_kinds]
            return obj != _EOL and self.kind in obj_kind_names
        return False
