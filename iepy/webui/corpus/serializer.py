from django.core.serializers.python import Serializer as BaseSerializer


class Serializer(BaseSerializer):

    def end_object(self, obj):
        # calls to obj.hydrate and attempts to add the missing fields. Only works with
        # explicit declaration of fields (not with fields=None)
        fields = self.selected_fields
        if fields is not None:
            missing = set(fields).difference(self._current.keys())
            if missing:
                obj.hydrate()
                _nothing = object()
                for f in missing:
                    fs = f.split('__')
                    value =
                    while fs:
                        value = getattr(value, fs.pop())

                    #value = getattr(obj, f, _nothing)
                    if value is not _nothing:
                        self._current[f] = value
        return super().end_object(obj)
