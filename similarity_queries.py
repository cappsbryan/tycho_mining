import MySQLdb
from datetime import datetime

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

state_codes = ['US-AL', 'US-AK', 'US-AZ', 'US-AR', 'US-CA', 'US-CO', 'US-CT', 'US-DE', 'US-FL', 'US-GA', 'US-HI',
               'US-ID', 'US-IL', 'US-IN', 'US-IA', 'US-KS', 'US-KY', 'US-LA', 'US-ME', 'US-MD', 'US-MA', 'US-MI',
               'US-MN', 'US-MS', 'US-MO', 'US-MT', 'US-NE', 'US-NV', 'US-NH', 'US-NJ', 'US-NM', 'US-NY', 'US-NC',
               'US-ND', 'US-OH', 'US-OK', 'US-OR', 'US-PA', 'US-RI', 'US-SC', 'US-SD', 'US-TN', 'US-TX', 'US-UT',
               'US-VT', 'US-VA', 'US-WA', 'US-WV', 'US-WI', 'US-WY']


def compute_similarity(disease1, disease2):
    date_range = compute_date_range()
    nonfatal_count = 0
    nonfatal_sum = 0
    fatal_count = 0
    fatal_sum = 0

    for state in state_codes:
        # nonfatal
        print(state, ': nonfatal:')
        state_count, state_sum = state_fatality_similarity(disease1, disease2, state, 0, date_range)
        nonfatal_count += state_count
        nonfatal_sum += state_sum

        # fatal
        print(state, ': fatal:')
        state_count, state_sum = state_fatality_similarity(disease1, disease2, state, 1, date_range)
        fatal_count += state_count
        fatal_sum += state_sum

        print(state, ': fatal_count =', fatal_count, '\tnonfatal_count =', nonfatal_count)
        print(state, ': fatal_sum   =', fatal_sum, '\tnonfatal_sum =', nonfatal_sum)

    # compute weighted average of fatal and nonfatal similarity scores
    nonfatal_similarity = 0 if nonfatal_count == 0 else nonfatal_sum/(2*nonfatal_count - nonfatal_sum)
    fatal_similarity = 0 if fatal_count == 0 else fatal_sum/(2*fatal_count - fatal_sum)
    print('nonfatal similarity:', nonfatal_similarity)
    print('fatal similarity:   ', fatal_similarity)
    similarity = ((nonfatal_count*nonfatal_similarity) + (fatal_count*fatal_similarity))/(nonfatal_count + fatal_count)

    return similarity


def compute_date_range():
    cursor = db_connection.cursor()
    cursor.execute("SELECT MIN(PeriodStartDate) FROM noncumulative_all_conditions;")
    min_datetime = datetime.combine(cursor.fetchone()[0], datetime.min.time())
    print('min_date:', min_datetime)
    cursor.execute("SELECT MAX(PeriodStartDate) FROM noncumulative_all_conditions;")
    max_datetime = datetime.combine(cursor.fetchone()[0], datetime.min.time())
    print('max_date:', max_datetime)
    date_range = (max_datetime - min_datetime).days
    print('date_range:', date_range)

    return date_range


def state_fatality_similarity(disease1_name, disease2_name, state, fatality, date_range):
    cursor = db_connection.cursor()
    cursor.execute("SELECT PeriodStartDate, CountValue FROM noncumulative_all_conditions WHERE ConditionName = '" +
                   disease1_name + "' AND Fatalities = " + str(fatality) + " AND Admin1ISO = '" + state + "';")
    disease1_data = cursor.fetchall()
    cursor.execute("SELECT PeriodStartDate, CountValue FROM noncumulative_all_conditions WHERE ConditionName = '" +
                   disease2_name + "' AND Fatalities = " + str(fatality) + " AND Admin1ISO = '" + state + "';")
    disease2_data = cursor.fetchall()

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
            similarity = row_similarity(shorter_item, longer_item, date_range)
            if similarity > max_similarity:
                max_similarity = similarity
                max_similarity_entry = longer_item

        # print(shorter_item, max_similarity_entry, max_similarity)
        similarity_sum += max_similarity
        longer_list.remove(max_similarity_entry)

    return similarity_count, similarity_sum


def row_similarity(row1, row2, date_range):
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
    similarity += min(count1/count2, count2/count1)

    # print('similarity:', similarity/2)
    return similarity/2
