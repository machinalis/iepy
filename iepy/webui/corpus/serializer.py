from django.core.serializers.python import Serializer as BaseSerializer


class Serializer(BaseSerializer):

    def end_object(self, obj):
        fields = self.selected_fields
        if fields is not None:
            missing = set(fields).difference(self._current.keys())
            if missing:
                _nothing = object()
                for f in missing:
                    fs = f.split('__')
                    value = obj
                    while fs:
                        value = getattr(value, fs.pop(0), _nothing)
                    if value is not _nothing:
                        self._current[f] = value
        return super().end_object(obj)

