from fuzzywuzzy import fuzz

#############
# Fuzzy match
#############
def fuzzy_group_words(words_list, fuzz_method=None, threshold=None):
    """
    fuzzy_group_words groups similar words into groups

    :param words_list: a list of words
    :type words_list: list
    :param fuzz_method: a fuzzywuzzy method, defaults to `fuzzywuzzy.partial_ratio`
    :param threshold: similarity threshold, defaults to 90
    :type threshold: int, optional
    :return: nested list of the grouped words
    :rtype: list
    """

    if fuzz_method is None:
        fuzz_method = fuzz.partial_ratio
    if threshold is None:
        threshold = 90

    words_fuzzy_group = []

    for i in words_list:
        words_fuzzy_group_i = [i]
        for j in words_list:
            fuzz_score = fuzz_method(i, j)
            if (fuzz_score >= threshold) & (j not in words_fuzzy_group_i):
                words_fuzzy_group_i.append(j)
        words_fuzzy_group.append(words_fuzzy_group_i)

    return words_fuzzy_group
