import MySQLdb
import pandas as pd
import os
from collections import defaultdict
from outlier_calc import top_outliers

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

def find_outliers(disease):
    print_valid_data(disease)
    #TODO Add query to get only locale info

def print_valid_data(disease):
    cursor = db_connection.cursor()
   # query_all_diseases = "SELECT City, State, SUM(CountValue) AS Fatalities, Occurences" \
   #              "FROM (SELECT CityName AS City, Admin1Name AS State, SUM(CountValue) AS Occurences" \
   #                  "FROM noncumulative_all_conditions " \
   #                  "WHERE CityName IS NOT NULL" \
   #                  "GROUP BY CityName)" \
   #              "WHERE Fatalities = 1" \
   #              "GROUP BY CityName"
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
    occ_knn_outliers = top_outliers(city_df.copy(), max_rows = 10, type="occurrence", method="knn")
    pct_normal_outliers = top_outliers(city_df.copy(), max_rows= 10, type="pct_fatal", method="normal")
    occ_normal_outliers = top_outliers(city_df.copy(), max_rows = 10, type="occurrence", method="normal")

    print(pct_normal_outliers)

def popular_conditions():
    '''

    :return:
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

def condition_names():
    """

    :return:
    """
    """
    cursor = db_connection.cursor()
    cursor.execute("SELECT ConditionName FROM noncumulative_all_conditions GROUP BY ConditionName")
    names = []
    for name in cursor.fetchall():
        names.append(name[0])
    print(names)
    return names
    """
    return ['Amebic dysentery', 'Anthrax', 'Babesiosis', 'Bacillary dysentery', 'Brucellosis', 'Chlamydia trachomatis infection', 'Chlamydial infection', 'Cholera', 'Coccidioidomycosis', 'Cryptosporidiosis', 'Dengue', 'Dengue hemorrhagic fever', 'Dengue without warning signs', 'Diphtheria', 'Dysentery', 'Human ehrlichiosis caused by Ehrlichia chaffeensis', 'Varicella', 'Encephalitis', 'Encephalitis lethargica', 'Giardiasis', 'Gonorrhea', 'Haemophilus influenzae infection', 'Human anaplasmosis caused by Anaplasma phagocytophilum', 'Infection caused by Escherichia coli', 'Infection caused by Shiga toxin producing Escherichia coli', 'Infective encephalitis', 'Inflammatory disease of liver', 'Post-infectious encephalitis', 'Primary encephalitis', 'Viral hepatitis', 'Viral hepatitis type B', 'Viral hepatitis, type A', 'Acute type A viral hepatitis', 'Acute type B viral hepatitis', 'Aseptic meningitis', 'Hepatitis non-A non-B', 'Influenza', 'Invasive meningococcal disease', 'Invasive Streptococcus pneumoniae disease', 'Legionella infection', 'Leprosy', 'Lyme disease', 'Malaria', 'Measles', 'Meningitis', 'Meningococcal infectious disease', 'Meningococcal meningitis', 'Mumps', 'Acute nonparalytic poliomyelitis', 'Acute paralytic poliomyelitis', 'Acute poliomyelitis', 'Infantile paralysis', 'Invasive Group A beta-hemolytic streptococcal disease', 'Lobar pneumonia', 'Ornithosis', 'Pellagra', 'Pneumonia', 'Rocky Mountain spotted fever', 'Rubella', 'Salmonella infection', 'Scarlet fever', 'Shigellosis', 'Smallpox', 'Spotted fever group rickettsial disease', 'Streptococcal sore throat', 'Active tuberculosis', 'Disorder of nervous system caused by West Nile virus', 'Infection caused by larvae of Trichinella', 'Invasive drug resistant Streptococcus pneumoniae disease', 'Murine typhus', 'Pertussis', 'Smallpox without rash', 'Tetanus', 'Toxic shock syndrome', 'Tuberculosis', 'Tularemia', 'Typhoid and paratyphoid fevers', 'Typhoid fever', 'Typhus group rickettsial disease', 'West Nile fever without encephalitis', 'Acute hepatitis C', 'Campylobacteriosis', 'Infection caused by non-cholerae vibrio', 'Yellow fever']

