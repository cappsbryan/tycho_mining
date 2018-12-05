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
    cursor = db_connection.cursor()
    query_end = ";" if state == "All" else " AND Admin1Name = '" + state + "';"
    query_disease1 = "SELECT PeriodStartDate, CountValue, Fatalities, Admin1Name FROM noncumulative_all_conditions " \
                     "WHERE ConditionName = '" + disease1_name + "' AND PeriodStartDate > " + \
                     start_date.replace('-', '') + " AND PeriodStartDate < " + end_date.replace('-', '') + query_end
    print(query_disease1)
    cursor.execute(query_disease1)
    disease1_data = cursor.fetchall()

    query_disease2 = "SELECT PeriodStartDate, CountValue, Fatalities, Admin1Name FROM noncumulative_all_conditions " \
                     "WHERE ConditionName = '" + disease2_name + "' AND PeriodStartDate > " + \
                     start_date.replace('-', '') + " AND PeriodStartDate < " + end_date.replace('-', '') + query_end
    print(query_disease2)
    cursor.execute(query_disease2)
    disease2_data = cursor.fetchall()

    print(disease1_name, ':', len(disease1_data), 'rows')
    print(disease2_name, ':', len(disease2_data), 'rows')

    if len(disease1_data) < len(disease2_data):
        shorter_list = disease1_data
        longer_list = list(disease2_data)
    else:
        shorter_list = disease2_data
        longer_list = list(disease1_data)

    similarity_count = len(shorter_list)
    similarity_sum = 0

    for shorter_item in shorter_list:
        max_similarity = 0
        max_similarity_entry = None
        for longer_item in longer_list:
            similarity = row_similarity(shorter_item, longer_item, state == "All")
            if similarity > max_similarity:
                max_similarity = similarity
                max_similarity_entry = longer_item

        # print(shorter_item, max_similarity_entry, max_similarity)
        similarity_sum += max_similarity
        longer_list.remove(max_similarity_entry)

    return similarity_count, similarity_sum


def row_similarity(row1, row2, compare_state):
    global date_range
    # print('computing similarity between rows:')
    # print(row1)
    # print(row2)
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

    # print('similarity:', similarity/len(row1))
    return similarity/len(row1)


def get_condition_names():
    return ['Amebic dysentery', 'Anthrax', 'Babesiosis', 'Bacillary dysentery', 'Brucellosis',
            'Chlamydia trachomatis infection', 'Chlamydial infection', 'Cholera', 'Coccidioidomycosis',
            'Cryptosporidiosis', 'Dengue', 'Dengue hemorrhagic fever', 'Dengue without warning signs', 'Diphtheria',
            'Dysentery', 'Human ehrlichiosis caused by Ehrlichia chaffeensis', 'Varicella', 'Encephalitis',
            'Encephalitis lethargica', 'Giardiasis', 'Gonorrhea', 'Haemophilus influenzae infection',
            'Human anaplasmosis caused by Anaplasma phagocytophilum', 'Infection caused by Escherichia coli',
            'Infection caused by Shiga toxin producing Escherichia coli', 'Infective encephalitis',
            'Inflammatory disease of liver', 'Post-infectious encephalitis', 'Primary encephalitis', 'Viral hepatitis',
            'Viral hepatitis type B', 'Viral hepatitis, type A', 'Acute type A viral hepatitis',
            'Acute type B viral hepatitis', 'Aseptic meningitis', 'Hepatitis non-A non-B', 'Influenza',
            'Invasive meningococcal disease', 'Invasive Streptococcus pneumoniae disease', 'Legionella infection',
            'Leprosy', 'Lyme disease', 'Malaria', 'Measles', 'Meningitis', 'Meningococcal infectious disease',
            'Meningococcal meningitis', 'Mumps', 'Acute nonparalytic poliomyelitis', 'Acute paralytic poliomyelitis',
            'Acute poliomyelitis', 'Infantile paralysis', 'Invasive Group A beta-hemolytic streptococcal disease',
            'Lobar pneumonia', 'Ornithosis', 'Pellagra', 'Pneumonia', 'Rocky Mountain spotted fever', 'Rubella',
            'Salmonella infection', 'Scarlet fever', 'Shigellosis', 'Smallpox',
            'Spotted fever group rickettsial disease', 'Streptococcal sore throat', 'Active tuberculosis',
            'Disorder of nervous system caused by West Nile virus', 'Infection caused by larvae of Trichinella',
            'Invasive drug resistant Streptococcus pneumoniae disease', 'Murine typhus', 'Pertussis',
            'Smallpox without rash', 'Tetanus', 'Toxic shock syndrome', 'Tuberculosis', 'Tularemia',
            'Typhoid and paratyphoid fevers', 'Typhoid fever', 'Typhus group rickettsial disease',
            'West Nile fever without encephalitis', 'Acute hepatitis C', 'Campylobacteriosis',
            'Infection caused by non-cholerae vibrio', 'Yellow fever']


def get_state_names():
    state_names_mod = deepcopy(list(state_names))
    state_names_mod.insert(0, 'All')
    return state_names_mod
