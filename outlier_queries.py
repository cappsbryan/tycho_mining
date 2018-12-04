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
date_range = 47313


def find_outliers(disease):
    print_valid_data(disease)
    #TODO Add query to get only locale info

def print_valid_data(disease):
    cursor = db_connection.cursor()
    if disease == "all":
        cursor.execute("SELECT CityName, SUM(Fatalities), SUM(CountValue), ConditionName FROM noncumulative_all_conditions WHERE CityName IS NOT NULL GROUP BY CityName")
    else:
        cursor.execute("SELECT CityName, SUM(Fatalities), SUM(CountValue) FROM noncumulative_all_conditions WHERE CityName IS NOT NULL AND ConditionName = '" + disease + "' GROUP BY CityName")
    cities = cursor.fetchall()
    print(cities)

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

