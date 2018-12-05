import MySQLdb
from datetime import datetime
from copy import deepcopy

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

state_names = ['Alabama', 'Alaska', 'American Samoa', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut',
               'Delaware', 'District of Colombia', 'Florida', 'Georgia', 'Guam', 'Hawaii', 'Idaho', 'Illinois',
               'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan',
               'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
               'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Northern Mariana Islands', 'Ohio',
               'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee',
               'Texas', 'Utah', 'Vermont', 'Virgin Islands, U.S.', 'Virginia', 'Washington', 'West Virginia',
               'Wisconsin', 'Wyoming']

date_range = 47313


def compute_similarity(disease1, disease2, state, start_date, end_date):
    global date_range
    print('computing similarity between', disease1, 'and', disease2)

    # compute similarity scores
    similarity_count, similarity_sum = individual_similarity_sum(disease1, disease2, state, start_date, end_date)
    similarity = 0 if similarity_count == 0 else similarity_sum/(2*similarity_count - similarity_sum)

    print('similarity_count =', similarity_count, '\tsimilarity_sum =', similarity_sum)
    print('similarity:', similarity)

    return similarity


def individual_similarity_sum(disease1_name, disease2_name, state, start_date, end_date):
    """
    Sum similarity scores for pairs of records in a given location and date range
    :param disease1_name: Name of the first disease
    :param disease2_name: Name of the second disease
    :param state: state in which to search
    :param start_date: earliest date
    :param end_date: latest date
    :return: the sum of the similarity scores
    """
    cursor = db_connection.cursor()

    # find all records for the first condition
    query_end = ";" if state == "All" else " AND Admin1Name = '" + state + "';"
    query_disease1 = "SELECT PeriodStartDate, CountValue, Fatalities, Admin1Name FROM noncumulative_all_conditions " \
                     "WHERE ConditionName = '" + disease1_name + "' AND PeriodStartDate > " + \
                     start_date.replace('-', '') + " AND PeriodStartDate < " + end_date.replace('-', '') + query_end
    print(query_disease1)
    cursor.execute(query_disease1)
    disease1_data = cursor.fetchall()

    # find all records for the second condition
    query_disease2 = "SELECT PeriodStartDate, CountValue, Fatalities, Admin1Name FROM noncumulative_all_conditions " \
                     "WHERE ConditionName = '" + disease2_name + "' AND PeriodStartDate > " + \
                     start_date.replace('-', '') + " AND PeriodStartDate < " + end_date.replace('-', '') + query_end
    print(query_disease2)
    cursor.execute(query_disease2)
    disease2_data = cursor.fetchall()

    print(disease1_name, ':', len(disease1_data), 'rows')
    print(disease2_name, ':', len(disease2_data), 'rows')

    # determine which disease has more records
    if len(disease1_data) < len(disease2_data):
        shorter_list = disease1_data
        longer_list = list(disease2_data)
    else:
        shorter_list = disease2_data
        longer_list = list(disease1_data)

    similarity_count = len(shorter_list)
    similarity_sum = 0

    # compute similarity scores for pairs of records
    for shorter_item in shorter_list:
        max_similarity = 0
        max_similarity_entry = None
        for longer_item in longer_list:
            similarity = row_similarity(shorter_item, longer_item, state == "All")
            if similarity > max_similarity:
                max_similarity = similarity
                max_similarity_entry = longer_item

        similarity_sum += max_similarity
        longer_list.remove(max_similarity_entry)

    return similarity_count, similarity_sum


def row_similarity(row1, row2, compare_state):
    """
    Compute similarity between two rows by normalizing the attribute differences
    :param row1: The first row
    :param row2: Th second row
    :param compare_state: True if location should be considered in the comparison
    :return: a similarity score in the range [0, 1]
    """
    global date_range
    similarity = 0

    # PeriodStartDate
    date1 = datetime.combine(row1[0], datetime.min.time())
    date2 = datetime.combine(row2[0], datetime.min.time())
    date_diff = abs((date1 - date2).days)
    similarity += (date_range - date_diff)/date_range

    # CountValue
    count1 = float(row1[1])
    count2 = float(row2[1])
    if count1 > 0 and count2 > 0:
        similarity += min(count1/count2, count2/count1)

    # Fatality
    if row1[2] == row2[2]:
        similarity += 1

    # Admin1Name
    if compare_state and row1[3] == row2[3]:
        similarity += 1

    return similarity/len(row1)


def get_condition_names():
    return ['Active tuberculosis', 'Acute hepatitis C', 'Acute nonparalytic poliomyelitis',
            'Acute paralytic poliomyelitis', 'Acute poliomyelitis', 'Acute type A viral hepatitis',
            'Acute type B viral hepatitis', 'Amebic dysentery', 'Anthrax', 'Aseptic meningitis', 'Babesiosis',
            'Bacillary dysentery', 'Brucellosis', 'Campylobacteriosis', 'Chlamydia trachomatis infection',
            'Chlamydial infection', 'Cholera', 'Coccidioidomycosis', 'Cryptosporidiosis', 'Dengue',
            'Dengue hemorrhagic fever', 'Dengue without warning signs', 'Diphtheria',
            'Disorder of nervous system caused by West Nile virus', 'Dysentery', 'Encephalitis',
            'Encephalitis lethargica', 'Giardiasis', 'Gonorrhea', 'Haemophilus influenzae infection',
            'Hepatitis non-A non-B', 'Human anaplasmosis caused by Anaplasma phagocytophilum',
            'Human ehrlichiosis caused by Ehrlichia chaffeensis', 'Infantile paralysis',
            'Infection caused by Escherichia coli', 'Infection caused by Shiga toxin producing Escherichia coli',
            'Infection caused by larvae of Trichinella', 'Infection caused by non-cholerae vibrio',
            'Infective encephalitis', 'Inflammatory disease of liver', 'Influenza',
            'Invasive Group A beta-hemolytic streptococcal disease', 'Invasive Streptococcus pneumoniae disease',
            'Invasive drug resistant Streptococcus pneumoniae disease', 'Invasive meningococcal disease',
            'Legionella infection', 'Leprosy', 'Lobar pneumonia', 'Lyme disease', 'Malaria', 'Measles', 'Meningitis',
            'Meningococcal infectious disease', 'Meningococcal meningitis', 'Mumps', 'Murine typhus', 'Ornithosis',
            'Pellagra', 'Pertussis', 'Pneumonia', 'Post-infectious encephalitis', 'Primary encephalitis',
            'Rocky Mountain spotted fever', 'Rubella', 'Salmonella infection', 'Scarlet fever', 'Shigellosis',
            'Smallpox', 'Smallpox without rash', 'Spotted fever group rickettsial disease', 'Streptococcal sore throat',
            'Tetanus', 'Toxic shock syndrome', 'Tuberculosis', 'Tularemia', 'Typhoid and paratyphoid fevers',
            'Typhoid fever', 'Typhus group rickettsial disease', 'Varicella', 'Viral hepatitis',
            'Viral hepatitis type B', 'Viral hepatitis, type A', 'West Nile fever without encephalitis', 'Yellow fever']


def get_state_names():
    state_names_mod = deepcopy(list(state_names))
    state_names_mod.insert(0, 'All')
    return state_names_mod
