from featureforge.feature import output_schema


@output_schema({str})
def bag_of_left_entity_IOB_chain(datapoint):
    print (hash(datapoint))
    eo = datapoint.left_entity_occurrence
    return set()


def _bag_of_eo_IOB_chain(datapoint, eo):
    tokens = datapoint.segment.tokens
    eo_tokens = tokens[eo.segment_offset: eo.segment_offset_end]
    result = set()
    lex_trees = datapoint.segment.let_trees
    if not lex_trees:
        return set()  # was not parsed on preprocess
    sentences = datapoint.segment.sentences
    for idx, eo_tk in enumerate(eo_tokens, eo.segment_offset):
        sentence = max(filter(lambda x: x<=idx, sentences))
        sentence_idx = sentences.index(sentence)
        tree = lex_trees[sentence_idx]
        tk_actual_idx = idx - sentence
        assert tk_actual_idx >= 0
        path = tree.leaf_treeposition(tk_actual_idx)
        #chain = 
