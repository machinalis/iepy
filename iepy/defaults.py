# In this file we have defined the default values for IEPY settings
# These default values will be always used except explicitely said.
from iepy.utils import make_feature_list


extractor_config = {
    "classifier": "svm",
    "classifier_args": {"probability": True},
    "dimensionality_reduction": None,
    "dimensionality_reduction_dimension": None,
    "feature_selection": None,
    "feature_selection_dimension": None,
    "scaler": True,
    "sparse": False,
    "features": make_feature_list("""
            bag_of_words
            bag_of_pos
            bag_of_word_bigrams
            bag_of_wordpos
            bag_of_wordpos_bigrams
            bag_of_words_in_between
            bag_of_pos_in_between
            bag_of_word_bigrams_in_between
            bag_of_wordpos_in_between
            bag_of_wordpos_bigrams_in_between
            entity_order
            entity_distance
            other_entities_in_between
            in_same_sentence
            verbs_count_in_between
            verbs_count
            total_number_of_entities
            symbols_in_between
            number_of_tokens
            BagOfVerbStems True
            BagOfVerbStems False
            BagOfVerbLemmas True
            BagOfVerbLemmas False
    """),
}
