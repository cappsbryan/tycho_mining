import csv
import itertools
from collections import defaultdict
from functools import reduce
from typing import Tuple, Dict, FrozenSet, Set, List, Any

import MySQLdb

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

ItemSet = FrozenSet[str]
Rule = Tuple[FrozenSet[str], FrozenSet[str]]
ListRule = List[List[str]]


def association_rules(min_support: float, min_confidence: float, max_size: int) -> Dict[str, List[Dict[str, Any]]]:
    diseases_dict = diseases_at_time_and_place()
    write_file(diseases_dict)
    transactions = list(diseases_dict.values())
    frequent, supports = apriori(min_support, max_size, transactions)
    rules = rule_generation(frequent)
    confidences = top_rules(rules, min_confidence, transactions, supports)
    return reformat_rules_for_json(confidences)


def reformat_rules_for_json(confidences: Dict[Rule, float]):
    rules = []
    for rule in confidences:
        rule_dict = {
            "x": sorted(rule[0]),
            "y": sorted(rule[1]),
            "confidence": confidences[rule]
        }
        rules.append(rule_dict)
    return {"rules": rules}


def diseases_at_time_and_place() -> Dict[Tuple[str, int], FrozenSet[str]]:
    """
    Gets all possible combinations of Admin1Name (state name) and Year.
    Using these combos, find all the diseases that were detected at the place at that time.
    Also make sure the disease meets the threshold count in the given amount of time.
    Returns a dictionary from time, place combo to set of diseases that occurred there
    :return: dict where keys are tuples of string and int and values are frozen sets of strings
    """
    all_diseases = defaultdict(lambda: frozenset())
    cursor = db_connection.cursor()

    # For cumulative, there exists a record for the whole year, so we find those using a combination
    # of the number of days between PeriodStartDate and PeriodEndDate (the DATEDIFF call)
    # and finding the average date between the start and end to get the most accurate year for the range
    cursor.execute("SELECT Admin1Name, "
                   "EXTRACT(YEAR FROM DATE_ADD(PeriodStartDate, "
                   "INTERVAL DATEDIFF(PeriodEndDate, PeriodStartDate) / 2 DAY)) Year, "
                   "ConditionName "
                   "FROM cumulative_all_conditions "
                   "WHERE CAST(CountValue AS DECIMAL) > 200 "
                   "AND DATEDIFF(PeriodEndDate, PeriodStartDate) BETWEEN 360 AND 370 "
                   "ORDER BY Year, Admin1Name, ConditionName")
    update_diseases(all_diseases, cursor)

    # For noncumulative, we just sum up all the records with PeriodEndDate in a certain year at a place
    # and use that as the count to check against the threshold. We use the year of PeriodEndDate as the year.
    cursor.execute("SELECT Admin1Name, EXTRACT(YEAR FROM PeriodEndDate) Year, ConditionName, SUM(CountValue) Count "
                   "FROM noncumulative_all_conditions "
                   "GROUP BY Admin1Name, Year, ConditionName "
                   "HAVING SUM(CAST(CountValue AS DECIMAL)) > 200 "
                   "ORDER BY Year, Admin1Name, ConditionName;")
    update_diseases(all_diseases, cursor)

    return all_diseases


def update_diseases(all_diseases: Dict[Tuple[str, int], FrozenSet[str]], cursor: MySQLdb.cursors.Cursor):
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


def write_file(all_diseases: Dict[Tuple[str, int], FrozenSet[str]]):
    """
    Write all_diseases to a file
    :param all_diseases: dict from tuple of str and int to frozen set of strings
    """
    with open('/Users/bryancapps/Desktop/disease_transactions.csv', 'wt', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for pair, diseases in all_diseases.items():
            writer.writerow([pair[0], pair[1], len(diseases)] + list(diseases))


def apriori(min_support: float, max_n: int, transactions: List[ItemSet]) -> (Set[ItemSet], Dict[ItemSet, int]):
    """
    Run the apriori algorithm to get frequent item sets
    Returns a set of the frequent item sets
    :param min_support: minimum support needed for a item set to be considered frequent
    :param max_n: maximum size of the returned item sets
    :param transactions: list of "purchased" item sets
    :return: set of frozen sets of strings
    """
    supports: Dict[ItemSet, int] = defaultdict(lambda: 0)
    frequent_sets = set()
    k = 0
    # F is a set of frequent itemsets
    # each iteration below adds a set of k-itemsets
    # i is a single itemset
    n = len(transactions)
    frequents_k = frequent_one_itemsets(min_support, transactions, supports)
    frequent_sets.update(frequents_k)
    while len(frequents_k) > 0 and k < max_n - 1:
        print('k =', k)
        k += 1
        candidates_k = gen_candidates(frequents_k)  # candidate itemsets of size k from previous Fk
        for transaction in transactions:
            candidates_t = candidates_in_transaction(candidates_k, transaction)
            for c in candidates_t:  # for each candidate itemset in the transaction, increment support
                supports[c] = 1 + supports[c]
        frequents_k = [c for c in candidates_k if supports[c] >= n * min_support]
        frequent_sets.update(frequents_k)
    return frequent_sets, supports


def frequent_one_itemsets(minsup: float, transactions, supports: Dict[ItemSet, int]) -> Set[ItemSet]:
    """
    Returns one item sets with at least minsup support in transactions
    Also updates supports with the support values calculated
    :param minsup: minimum support needed for a item set to be considered frequent
    :param transactions: list of "purchased" item sets
    :param supports: dict from item set to count of that item set
    :return:
    """
    for transaction in transactions:
        for item in transaction:
            one_itemset = frozenset([item])
            supports[one_itemset] += 1
    return set(filter(lambda itemset: supports[itemset] >= len(transactions) * minsup, supports.keys()))


def calculate_support(itemset: ItemSet, transactions, supports: Dict[ItemSet, int]) -> float:
    """
    Calculate the support of a given itemset in the given transactions
    Also saves the support value to the given supports dict
    item set must be sorted, each transaction should already be sorted
    """
    count = 0
    for transaction in transactions:
        itemset_in_transaction = True
        for item in itemset:
            if item not in transaction:
                itemset_in_transaction = False
                break
        if itemset_in_transaction:
            count += 1
    supports[itemset] = count
    return count


def find_support(itemset: ItemSet, transactions, supports) -> float:
    """
    Returns the support for the itemset from the supports dict if present
    or calculates the support
    :param itemset: the itemset to find the support of
    :param transactions: list of "purchased" item sets
    :param supports: dict from item set to support of that item set
    :return: float of the support of the itemset in transactions
    """
    if itemset in supports:
        return supports[itemset]
    else:
        return calculate_support(itemset, transactions, supports)


def gen_candidates(prev_sets: Set[ItemSet]) -> Set[ItemSet]:
    """
    Generate the candidate item sets of size k based on prev_sets, a set of frequent item sets of size k-1
    :param prev_sets: set of item sets all of size k-1
    :return: set of item sets of size k
    """
    itemsets = set()
    k = len(next(iter(prev_sets))) + 1  # length of candidate itemsets we are generating
    for set_a, set_b in itertools.combinations(prev_sets, 2):
        list_a, list_b = sorted(set_a), sorted(set_b)
        if list_a[:k - 2] != list_b[:k - 2] or list_a[k - 2] == list_b[k - 2]:
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


def candidates_in_transaction(candidates_k: Set[ItemSet], transaction: ItemSet) -> Set[ItemSet]:
    """
    Returns all the candidate item sets in the given transaction
    :param candidates_k: the candidate item sets to look for
    :param transaction: a single transaction of "purchased" items
    :return: candidate item sets from Ck that are in transaction
    """
    candidates = set()
    example_candidate = next(iter(candidates_k))
    k = len(example_candidate)
    for subset in itertools.combinations(transaction, k):
        frozen_subset = frozenset(subset)
        if frozen_subset in candidates_k:
            candidates.add(frozen_subset)
    return candidates


def rule_generation(frequents: Set[FrozenSet[str]]) -> List[Rule]:
    """
    Generate rules from frequent item sets
    :param frequents: frequent item sets
    :return: list of tuples where the first item set implies the second item set
    """
    rules = []
    for i, L in enumerate(frequents):
        for r in range(1, len(L)):
            for f in itertools.combinations(L, r):
                f = frozenset(f)
                l_f = L - f
                rules.append((f, l_f))
    return rules


def top_rules(rules: List[Rule], min_confidence: float, transactions, supports) -> Dict[Rule, float]:
    all_confidences = {rule: rule_confidence(rule, transactions, supports) for rule in rules}
    sorted_confidences = sorted(all_confidences.items(), key=lambda kv: kv[1], reverse=True)
    top_confidences = [item for item in sorted_confidences if item[1] >= min_confidence]
    return dict(top_confidences)


def rule_confidence(rule: Rule, transactions, supports):
    x, y = rule
    return find_support(x.union(y), transactions, supports) / find_support(x, transactions, supports)


def prettify_rules(confidences: Dict[Rule, float]) -> List[str]:
    strings = '\n'
    for i, rule in enumerate(sorted(confidences)):
        rule_string = prettify_rule(rule)
        strings += rule_string.ljust(100) + str(confidences[rule]).rjust(10) + '\n'
    return strings


def prettify_rule(rule):
    return prettify_itemset(rule[0]) + ' -> ' + prettify_itemset(rule[1])


def prettify_itemset(itemset):
    string = '{ '
    for i, item in enumerate(itemset):
        string += "'" + item + "'"
        if i != len(itemset) - 1:
            string += ", "
    string += ' }'
    return string


def arm_amo(transactions: List[ItemSet]):
    diseases = sorted(reduce(lambda s1, s2: s1.union(s2), transactions))
    binary_values = []


if __name__ == '__main__':
    diseases_dict = diseases_at_time_and_place()
    transactions = list(diseases_dict.values())
    arm_amo(transactions)
