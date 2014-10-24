# In this file we have defined the default values for IEPY settings
# These default values will be always used except explicitely said.
from iepy.utils import make_feature_list


extractor_config = {
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
