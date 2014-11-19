import ast

from nltk.tree import Tree
from django.db import models


class ListField(models.TextField, metaclass=models.SubfieldBase):
    description = "Python list"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class ListSyntacticTreeField(models.TextField, metaclass=models.SubfieldBase):
    description = "List of Stanford syntactic tree"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        xs = ast.literal_eval(value)
        return [Tree.fromstring(x) for x in xs]

    def get_prep_value(self, value):
        if value is None:
            return value

        if isinstance(value, list):
            return str([str(x) for x in value])

        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
