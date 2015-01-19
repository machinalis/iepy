from unittest import mock

from iepy.extraction import rules
from iepy.data.models import RichToken

from .manager_case import ManagerTestCase
from .factories import EvidenceFactory


class TestCachedSegmentEnrichedTokens(ManagerTestCase):
    def setUp(self):
        rules._cache = {}
        self.s1 = EvidenceFactory(markup="The physicist "
                                  "{Albert Einstein|Person*} was born in "
                                  "{Germany|location} and died in the "
                                  "{United States|location**}"
                                  " .").segment.hydrate()
        self.s2 = EvidenceFactory(markup="The little dog {Terry|Dog} happily "
                                  "eats his food in {Babaria|location} while "
                                  "the blond, pale kids sing creepy "
                                  "stuff .").segment.hydrate()

    def test_simple(self):
        xs = rules.cached_segment_enriched_tokens(self.s1)
        self.assertTrue(isinstance(xs, list))
        self.assertTrue(all(isinstance(x, RichToken) for x in xs))

    def test_cache_works_1(self):
        xs = rules.cached_segment_enriched_tokens(self.s1)
        rules.cached_segment_enriched_tokens(self.s2)
        ys = rules.cached_segment_enriched_tokens(self.s1)
        self.assertTrue(xs is ys)

    def test_cache_works_2(self):
        mockedGET = mock.MagicMock(return_value=self.s1.get_enriched_tokens())
        self.s1.get_enriched_tokens = mockedGET
        rules.cached_segment_enriched_tokens(self.s1)
        rules.cached_segment_enriched_tokens(self.s1)
        mockedGET.assert_called_once_with()
