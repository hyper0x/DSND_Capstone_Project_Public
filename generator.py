from collections import defaultdict


def gen_id_map(id_col):
    """Generates a map for ID.
    The keys are the original ID and the values are the new integer ID.
    """
    coded_dict = defaultdict(int)
    counter = 1

    for id in id_col:
        if id not in coded_dict:
            coded_dict[id] = counter
            counter += 1

    return coded_dict
