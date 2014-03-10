import contextlib
import datetime


class Timer(object):

    def start(self):
        self.start = datetime.datetime.now()

    def stop(self):
        self.stop = datetime.datetime.now()

    def elapsed(self):
        return self.stop - self.start

    def assertHasDate(self, date):
        assert self.start <= date <= self.stop, "%s was not during the timer" % date

    def assertNotHasDate(self, date):
        assert not (self.start <= date <= self.stop), "%s was during the timer" % date


@contextlib.contextmanager
def timekeeper():
    t = Timer()
    t.start()
    try:
        yield t
    finally:
        t.stop()
