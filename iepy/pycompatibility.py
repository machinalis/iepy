import sys
import contextlib
PY2 = sys.version < '3'

if PY2:
    from unicodecsv import DictReader, writer
else:
    from csv import DictReader, writer

ENCODING = u'utf-8'

class PyCompatibilityCSV(object):

    def utf8_opener(self, mode, file_path):
        open_kwargs = {'mode': mode, 'encoding': ENCODING}
        if PY2:
            open_kwargs.pop('encoding')
        return open(file_path, **open_kwargs)

    @contextlib.contextmanager
    def writer(self, file_path):
        with self.utf8_opener('wt', file_path) as utf8_file:
            yield writer(utf8_file, delimiter=',')

    @contextlib.contextmanager
    def DictReader(self, file_path, fieldnames):
        with self.utf8_opener('rt', file_path) as utf8_file:
            yield DictReader(utf8_file, fieldnames=fieldnames)


py_compatible_csv = PyCompatibilityCSV()