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


#######

def walk_tree(tree, path):
    result = tree
    for i in path:
        result = result[i]
    return result


def chunk_tag(evidence):
    result = set()
    tree = evidence.segment.lex_trees[0]
    for i, _ in enumerate(tree.leaves()):
        path = tree.leaf_treeposition(i)
        parent = walk_tree(tree, path[:-2])
        parent_label = parent.label()

        position_in_sentence = path[-2]
        if parent_label == "S":
            tag = "O"
        else:
            modifier = "B" if position_in_sentence == 0 else "I"
            tag = "{}-{}".format(modifier, parent_label)

        result.add(tag)

    return result


def iob_chain(evidence):
    result = set()
    tree = evidence.segment.lex_trees[0]
    for i, _ in enumerate(tree.leaves()):
        path = tree.leaf_treeposition(i)[:-1]
        chain = []
        subtree = tree
        for (step, next_step) in zip(path, path[1:]):
            subtree = subtree[step]
            modifier = "B" if next_step == 0 else "I"
            tag = "{}-{}".format(modifier, subtree.label())
            chain.append(tag)
        result.add("/".join(chain))
    return result
