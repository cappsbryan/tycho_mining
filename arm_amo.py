import itertools
import math
from datetime import datetime
from functools import reduce
from typing import Set, List, Collection

import numpy as np

from association_rules import ItemSet, gen_candidates, diseases_at_time_and_place, association_rules, BinaryItemSet, \
    BinaryRule


def arm_amo(min_support: float, min_confidence: float, transactions: List[ItemSet]):
    t = 0
    binary_data = make_binary(transactions)
    rules = apriori_rules(min_support, min_confidence, binary_data)
    net_f = net_fitness(rules, binary_data)
    fitnesses = [fit(rule, binary_data) for rule in rules]
    glob_min_support = sum(support(set.union(*rule), binary_data) for rule in rules)


def make_binary(transactions):
    all_diseases = sorted(reduce(lambda x, y: x.union(y), transactions))
    n_diseases = len(all_diseases)
    disease_to_index = {disease: i for i, disease in enumerate(all_diseases)}
    indexed_transactions = [{disease_to_index[disease] for disease in transaction} for transaction in transactions]
    binary_transactions = [indexes_to_binary_list(indexes, n_diseases) for indexes in indexed_transactions]
    return np.array(binary_transactions)


def apriori_rules(min_support, min_confidence, binary_data: np.ndarray):
    frequent_sets: Set[BinaryItemSet] = set()
    k = 0
    # F is a set of frequent itemsets
    # each iteration k below adds a set of k-itemsets
    row_size = binary_data.shape[1]
    frequents_k = {frozenset([i]) for i in range(row_size) if support([i], binary_data) > min_support}
    frequent_sets.update(frequents_k)
    while len(frequents_k) > 0 and k < row_size - 1:
        print('k =', k)
        k += 1
        candidates_k = gen_candidates(frequents_k)  # candidate itemsets of size k from previous Fk
        frequents_k = [c for c in candidates_k if support(c, binary_data) >= min_support]
        frequent_sets.update(frequents_k)

    rules = []
    for i, L in enumerate(frequent_sets):
        for r in range(1, len(L)):
            for f in itertools.combinations(L, r):
                f = frozenset(f)
                l_f = L - f
                rules.append((f, l_f))

    all_confidences = {rule: rule_confidence(rule, binary_data) for rule in rules}
    sorted_confidences = sorted(all_confidences.items(), key=lambda kv: kv[1], reverse=True)
    top_confidences = [item for item in sorted_confidences if item[1] >= min_confidence]
    return list(top_confidences)


def overall_fitness(rule: BinaryRule, data: np.ndarray):
    numerator = math.log(rule_confidence(rule, data) + support(set.union(*rule), data))
    denominator = math.log(rule_confidence(rule, data)) + math.log(support(set.union(*rule), data))
    return numerator / denominator


def net_fitness(rules: Collection[BinaryRule], data: np.ndarray):
    s = sum(overall_fitness(rule, data) for rule in rules)
    fitness = s / len(rules)
    return fitness


def fit(rule: BinaryRule, data: np.ndarray):
    xy = set.union(*rule)
    return rule_confidence(rule, data) * math.log1p(support(xy, data) * len(xy))


def indexes_to_binary_list(indexes, n):
    return [1 if i in indexes else 0 for i in range(n)]


def support(x: Collection[int], binary_data: np.ndarray):
    """
    Support of an itemset in the transactions represented by binary_data
    :param x: list of the indexes of the diseases in the itemset
    :param binary_data: matrix where every row is a transaction and every column is a disease, elements are 1 if disease
    is in transaction, 0 otherwise
    :return: support of itemset x in transactions binary data
    """
    cols = [binary_data[:, xi] for xi in x]
    zipped_cols = zip(*cols)
    transactions_containing_x = sum(1 for row in zipped_cols if all(row))
    return transactions_containing_x / binary_data.shape[0]


def rule_confidence(rule: BinaryRule, binary_data: np.ndarray):
    """
    Confidence of a rule (x -> y) in the transactions represented by binary_data
    :param rule: a tuple where the first element is the set of indexes for the left side of the rule (x) and the
    second element is the set of indexes for the right side of the rule (y)
    :param binary_data: matrix where every row is a transaction and every column is a disease, elements are 1 if disease
    is in transaction, 0 otherwise
    :return: confidence of the rule (or, proportion of transactions containing x that also contain y)
    """
    x, y = rule
    sup_xy = support(x.union(y), binary_data)
    sup_x = support(x, binary_data)
    return sup_xy / sup_x


def candidates_in_transaction(candidates: Set[BinaryItemSet], transaction: np.ndarray):
    """
    Returns all the candidate item sets in the given transaction
    :param candidates: the candidate item sets to look for, items are indexes that correspond to diseases
    :param transaction: a single transaction of "purchased" items, elements are 1 if disease with the same index
    is in transaction, 0 otherwise
    :return: candidate item sets from candidates that are in transaction
    """
    return {candidate for candidate in candidates if all([transaction[item] for item in candidate])}


def run_arm_amo():
    before = datetime.now()
    diseases_dict = diseases_at_time_and_place()
    print('query took', (datetime.now() - before).seconds, 'seconds')
    before = datetime.now()
    transactions = list(diseases_dict.values())
    arm_amo(0.05, 0.9, transactions)
    print('arm-amo took', (datetime.now() - before).seconds, 'seconds')
    # old way:
    before = datetime.now()
    association_rules(0.05, 0.9, 3)
    print('apriori took', (datetime.now() - before).seconds, 'seconds')


if __name__ == '__main__':
    run_arm_amo()
