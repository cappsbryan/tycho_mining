import MySQLdb
import pandas as pd
from collections import defaultdict
from outlier_calc import top_outliers

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

def find_outliers(disease):
    '''
    Takes a disease and returns outlier cities and their info
    :param disease: string, disease in database or "all"
    :return: 6 pandas dataframes containing outlier cities
    '''
    cities = defaultdict(dict)
    if disease == "all":
        query = "SELECT * FROM (" \
                "SELECT CityName, Admin1Name, Fatalities, SUM(CountValue) AS Occurences " \
                         "FROM noncumulative_all_conditions " \
                         "WHERE CityName IS NOT NULL " \
                         "GROUP BY CityName, Admin1Name, Fatalities) a " \
                "WHERE Occurences >= 10"
    else:
        query = "SELECT * FROM (" \
                "SELECT CityName, Admin1Name, Fatalities, SUM(CountValue) AS Occurences" \
                             " FROM noncumulative_all_conditions " \
                             "WHERE CityName IS NOT NULL AND ConditionName = '" + disease +"'" \
                             "GROUP BY ConditionName, CityName, Admin1Name, Fatalities) a " \
                "WHERE Occurences >= 10"
    data = pd.read_sql(query, con=db_connection)
    for index, row in data.iterrows():
        key = (row["CityName"], row["Admin1Name"])
        if key not in cities:
            cities[key] = {"Fatalities": 0, "Occurences": 0}
        if row["Fatalities"] == 1:
            cities[key]["Fatalities"] += row["Occurences"]
            cities[key]["Occurences"] += row["Occurences"]
        else:
            cities[key]["Occurences"] += row["Occurences"]
    city_df = pd.DataFrame(cities).transpose()

    pct_knn_outliers = top_outliers(city_df.copy(), max_rows = 10, type="pct_fatal", method="knn")
    pct_normal_outliers = top_outliers(city_df.copy(), max_rows= 10, type="pct_fatal", method="normal")

    occ_knn_outliers = top_outliers(city_df.copy(), max_rows = 10, type="occurrence", method="knn")
    occ_normal_outliers = top_outliers(city_df.copy(), max_rows = 10, type="occurrence", method="normal")

    fatal_knn_outliers = top_outliers(city_df.copy(), max_rows = 10, type="fatalities", method="knn")
    fatal_normal_outliers = top_outliers(city_df.copy(), max_rows = 10, type="fatalities", method="normal")

    # outliers = {"knn_pct" : pct_knn_outliers, "knn_occ" : occ_knn_outliers, "knn_fatal" : fatal_knn_outliers,
    #             "normal_pct" : pct_normal_outliers, "normal_occ" : occ_normal_outliers, "normal_fatal" : fatal_normal_outliers}
    # return outliers
    return pct_knn_outliers, pct_normal_outliers, occ_knn_outliers, occ_normal_outliers, fatal_knn_outliers, fatal_normal_outliers

def popular_conditions():
    '''
    A list of prepopulated popular conditions to chooose from. We don't want to let the user select diseases without enough data for outliers to exist
    :return: the list
    '''
    '''
    cursor = db_connection.cursor()
    cursor.execute("SELECT ConditionName, COUNT(DISTINCT CityName) FROM noncumulative_all_conditions WHERE CityName IS NOT NULL GROUP BY ConditionName")
    names = []
    for name in cursor.fetchall():
        if name[1] > 10:
            names.append(name[0])
    print(names)
    '''
    return ['Acute poliomyelitis', 'Aseptic meningitis', 'Brucellosis', 'Cholera', 'Dengue', 'Diphtheria',
            'Encephalitis lethargica', 'Infantile paralysis', 'Infection caused by larvae of Trichinella',
            'Infective encephalitis', 'Influenza', 'Leprosy', 'Lobar pneumonia', 'Malaria', 'Measles', 'Meningitis',
            'Meningococcal infectious disease', 'Meningococcal meningitis', 'Mumps', 'Murine typhus', 'Pellagra',
            'Pertussis', 'Pneumonia', 'Rocky Mountain spotted fever', 'Scarlet fever', 'Smallpox',
            'Smallpox without rash', 'Tuberculosis', 'Tularemia', 'Typhoid and paratyphoid fevers', 'Typhoid fever',
            'Typhus group rickettsial disease', 'Varicella', 'Viral hepatitis', 'Viral hepatitis type B',
            'Viral hepatitis, type A', 'Yellow fever']