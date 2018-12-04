import csv
import itertools
import os
from collections import defaultdict
from functools import reduce
from typing import Tuple, Dict, FrozenSet, Set, List, Union, Collection

import MySQLdb
import numpy as np

# type definitions
StrItemSet = FrozenSet[str]
IndexItemSet = FrozenSet[int]
GenericItemSet = Union[StrItemSet, IndexItemSet]
StrRule = Tuple[StrItemSet, StrItemSet]
IndexRule = Tuple[FrozenSet[int], FrozenSet[int]]
StateYearPair = Tuple[str, int]

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)


def association_rules(min_support: float, min_confidence: float) -> Dict[StrRule, float]:
    """
    Find all the association rules fulfilling the minimum support and minimum confidence requirements
    :param min_support: the lower bound on the ratio of data points that contain the diseases in the rule
    to total data points for rules that should be included in the result
    :param min_confidence: the lower bound on the ratio of data points that contain both x and y
    to data points that contain x for rules (x to y) that should be included in the result
    :return:
    """
    diseases_dict = diseases_at_time_and_place()
    transactions = list(diseases_dict.values())
    binary_transactions = make_binary(transactions)
    frequent = apriori(min_support, binary_transactions)
    rules = rule_generation(frequent)
    confidences = top_rules(rules, min_confidence, binary_transactions, transactions)
    return confidences


def diseases_at_time_and_place() -> Dict[StateYearPair, StrItemSet]:
    """
    Gets all possible combinations of Admin1Name (state name) and Year.
    Using these combos, find all the diseases that were detected at the place at that time.
    Also make sure the disease meets the threshold count in the given amount of time.
    Returns a dictionary from time, place combo to set of diseases that occurred there
    :return: dict where keys are tuples of string and int and values are frozen sets of strings
    """
    path_to_cache_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'diseases_at_time_and_place.csv')
    try:
        return read_diseases_at_time_and_place_cache(path_to_cache_file)
    except OSError:
        pass

    all_diseases = defaultdict(lambda: frozenset())
    cursor = db_connection.cursor()

    threshold = 200

    # For cumulative, there exists a record for the whole year, so we find those using a combination
    # of the number of days between PeriodStartDate and PeriodEndDate (the DATEDIFF call)
    # and finding the average date between the start and end to get the most accurate year for the range
    cursor.execute("SELECT Admin1Name, "
                   "EXTRACT(YEAR FROM DATE_ADD(PeriodStartDate, "
                   "INTERVAL DATEDIFF(PeriodEndDate, PeriodStartDate) / 2 DAY)) Year, "
                   "ConditionName "
                   "FROM cumulative_all_conditions "
                   f"WHERE CAST(CountValue AS DECIMAL) > {threshold} "
                   "AND DATEDIFF(PeriodEndDate, PeriodStartDate) BETWEEN 360 AND 370 "
                   "ORDER BY Year, Admin1Name, ConditionName")
    update_diseases(all_diseases, cursor)

    # For noncumulative, we just sum up all the records with PeriodEndDate in a certain year at a place
    # and use that as the count to check against the threshold. We use the year of PeriodEndDate as the year.
    cursor.execute("SELECT Admin1Name, EXTRACT(YEAR FROM PeriodEndDate) Year, ConditionName, SUM(CountValue) Count "
                   "FROM noncumulative_all_conditions "
                   "GROUP BY Admin1Name, Year, ConditionName "
                   f"HAVING SUM(CAST(CountValue AS DECIMAL)) > {threshold} "
                   "ORDER BY Year, Admin1Name, ConditionName;")
    update_diseases(all_diseases, cursor)

    write_diseases_at_time_and_place_cache(all_diseases, path_to_cache_file)

    return all_diseases


def make_binary(transactions: List[StrItemSet]) -> np.ndarray:
    all_diseases = sorted(reduce(lambda x, y: x.union(y), transactions))
    n_diseases = len(all_diseases)
    disease_to_index = {disease: i for i, disease in enumerate(all_diseases)}
    indexed_transactions = [{disease_to_index[disease] for disease in transaction} for transaction in transactions]
    binary_transactions = [indexes_to_binary_list(indexes, n_diseases) for indexes in indexed_transactions]
    return np.array(binary_transactions)


def apriori(min_support: float, binary_data: np.ndarray) -> Set[IndexItemSet]:
    frequent_sets = set()
    k = 0
    # F is a set of frequent itemsets
    # each iteration k below adds a set of k-itemsets
    row_size = binary_data.shape[1]
    frequents_k = {frozenset([i]) for i in range(row_size) if support([i], binary_data) > min_support}
    frequent_sets.update(frequents_k)
    while len(frequents_k) > 0 and k < row_size - 1:
        k += 1
        candidates_k = gen_candidates(frequents_k)  # candidate itemsets of size k from previous Fk
        frequents_k = [c for c in candidates_k if support(c, binary_data) >= min_support]
        frequent_sets.update(frequents_k)
    return frequent_sets


def rule_generation(frequent_sets: Set[IndexItemSet]) -> List[IndexRule]:
    rules = []
    for i, L in enumerate(frequent_sets):
        for r in range(1, len(L)):
            for f in itertools.combinations(L, r):
                f = frozenset(f)
                l_f = L - f
                rules.append((f, l_f))
    return rules


def top_rules(rules: List[IndexRule], min_confidence: float, binary_data: np.ndarray,
              transactions: List[StrItemSet]) -> Dict[StrRule, float]:
    confidences = {rule: rule_confidence(rule, binary_data) for rule in rules}
    satisfactory_rules = [(rule, confidences[rule]) for rule in confidences if confidences[rule] > min_confidence]
    satisfactory_rules.sort(key=lambda rc: rc[1], reverse=True)
    str_rules = {index_rule_to_str_rule(r, transactions): c for r, c in satisfactory_rules}
    return str_rules


def index_rule_to_str_rule(index_rule: IndexRule, transactions) -> StrRule:
    all_diseases = sorted(reduce(lambda x, y: x.union(y), transactions))
    return tuple(frozenset(all_diseases[i] for i in side) for side in index_rule)


def update_diseases(all_diseases: Dict[StateYearPair, StrItemSet], cursor: MySQLdb.cursors.Cursor):
    """
    Fetches rows from cursor and updates all_diseases with the rows
    Doesn't return anything, but updates all_diseases directly
    :param all_diseases: dict from place and time to set of diseases at that time and place
    :param cursor: a database cursor with rows containing Admin1Name, Year, and ConditionName
    """
    current_row = cursor.fetchone()
    while current_row is not None:
        place_time = tuple(current_row[:2])
        disease = current_row[2]
        all_diseases[place_time] = all_diseases[place_time].union({disease})
        current_row = cursor.fetchone()


def read_diseases_at_time_and_place_cache(path_to_cache_file) -> Dict[StateYearPair, StrItemSet]:
    with open(path_to_cache_file, 'rt', newline='') as cache_file:
        reader = csv.reader(cache_file)
        all_diseases = dict()
        for row in reader:
            row[1], row[2] = int(row[1]), int(row[2])
            pair = (row[0], row[1])
            diseases = frozenset({row[i] for i in range(3, row[2] + 3)})
            all_diseases[pair] = diseases
        return all_diseases


def write_diseases_at_time_and_place_cache(all_diseases, path):
    with open(path, 'wt', newline='') as cache_file:
        writer = csv.writer(cache_file)
        for pair, diseases in all_diseases.items():
            writer.writerow([pair[0], pair[1], len(diseases)] + list(diseases))


def gen_candidates(prev_sets: Set[GenericItemSet]) -> Set[GenericItemSet]:
    """
    Generate the candidate item sets of size k based on prev_sets, a set of frequent item sets of size k-1
    :param prev_sets: set of item sets all of size k-1
    :return: set of item sets of size k
    """
    itemsets = set()
    k = len(next(iter(prev_sets))) + 1  # length of candidate itemsets we are generating
    for set_a, set_b in itertools.combinations(prev_sets, 2):
        list_a, list_b = sorted(set_a), sorted(set_b)
        if list_a[:-1] != list_b[:-1] or list_a[-1] == list_b[-1]:
            continue
        itemset = list_a + list_b[-1:]
        subsets_are_frequent = True
        for subset in itertools.combinations(itemset, k - 1):
            if frozenset(subset) not in prev_sets:
                subsets_are_frequent = False
                break
        if subsets_are_frequent:
            itemsets.add(frozenset(itemset))
    return itemsets


def rule_confidence(rule: IndexRule, binary_data: np.ndarray) -> float:
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


def indexes_to_binary_list(indexes, n):
    return [1 if i in indexes else 0 for i in range(n)]
