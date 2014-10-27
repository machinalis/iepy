# -*- coding: utf-8 -*-
from iepy.extraction.relation_extraction_classifier import RelationExtractionClassifier
from iepy.utils import make_feature_list

from .manager_case import ManagerTestCase


class TestFactExtractor(ManagerTestCase):
    def setUp(self):
        self.config = {
            "classifier": "svc",
            "classifier_args": {},
            "dense_features": make_feature_list("""
                entity_order
                entity_distance
                other_entities_in_between
                verbs_count_in_between
                verbs_count
                total_number_of_entities
                symbols_in_between
                number_of_tokens
                """),
            "sparse_features": make_feature_list("""
                bag_of_words
                bag_of_pos
                bag_of_words_in_between
                bag_of_pos_in_between
                """)
        }

    def test_simple_ok_configuration(self):
        RelationExtractionClassifier(**self.config)

    def test_error_missing_configuration(self):
        del self.config["dense_features"]
        with self.assertRaises(ValueError):
            RelationExtractionClassifier(**self.config)

    def test_error_nonexistent_feature(self):
        self.config["dense_features"].append("the_yeah_yeah_feature")
        with self.assertRaises(KeyError):
            RelationExtractionClassifier(**self.config)
