import datetime
import MySQLdb
import csv
import pprint

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)


def main():
    diseases = ["Active tuberculosis",
                "Acute hepatitis C",
                "Acute nonparalytic poliomyelitis",
                "Acute paralytic poliomyelitis",
                "Acute poliomyelitis",
                "Acute type A viral hepatitis",
                "Acute type B viral hepatitis",
                "Amebic dysentery",
                "Anthrax",
                "Aseptic meningitis",
                "Babesiosis",
                "Bacillary dysentery",
                "Brucellosis",
                "Campylobacteriosis",
                "Chlamydia trachomatis infection",
                "Chlamydial infection",
                "Cholera",
                "Coccidioidomycosis",
                "Cryptosporidiosis",
                "Dengue",
                "Dengue hemorrhagic fever",
                "Dengue without warning signs",
                "Diphtheria",
                "Disorder of nervous system caused by West Nile virus",
                "Dysentery",
                "Encephalitis",
                "Encephalitis lethargica",
                "Giardiasis",
                "Gonorrhea",
                "Haemophilus influenzae infection",
                "Hepatitis non-A non-B",
                "Human anaplasmosis caused by Anaplasma phagocytophilum",
                "Human ehrlichiosis caused by Ehrlichia chaffeensis",
                "Infantile paralysis",
                "Infection caused by Escherichia coli",
                "Infection caused by larvae of Trichinella",
                "Infection caused by non-cholerae vibrio",
                "Infection caused by Shiga toxin producing Escherichia coli",
                "Infective encephalitis",
                "Inflammatory disease of liver",
                "Influenza",
                "Invasive drug resistant Streptococcus pneumoniae disease",
                "Invasive Group A beta-hemolytic streptococcal disease",
                "Invasive meningococcal disease",
                "Invasive Streptococcus pneumoniae disease",
                "Legionella infection",
                "Leprosy",
                "Lobar pneumonia",
                "Lyme disease",
                "Malaria",
                "Measles",
                "Meningitis",
                "Meningococcal infectious disease",
                "Meningococcal meningitis",
                "Mumps",
                "Murine typhus",
                "Ornithosis",
                "Pellagra",
                "Pertussis",
                "Pneumonia",
                "Post-infectious encephalitis",
                "Primary encephalitis",
                "Rocky Mountain spotted fever",
                "Rubella",
                "Salmonella infection",
                "Scarlet fever",
                "Shigellosis",
                "Smallpox",
                "Smallpox without rash",
                "Spotted fever group rickettsial disease",
                "Streptococcal sore throat",
                "Tetanus",
                "Toxic shock syndrome",
                "Tuberculosis",
                "Tularemia",
                "Typhoid and paratyphoid fevers",
                "Typhoid fever",
                "Typhus group rickettsial disease",
                "Varicella",
                "Viral hepatitis",
                "Viral hepatitis type B",
                "Viral hepatitis, type A",
                "West Nile fever without encephalitis",
                "Yellow fever"]

    states = ["WISCONSIN",
              "OHIO",
              "MICHIGAN",
              "NEVADA",
              "NEW JERSEY",
              "WASHINGTON",
              "DELAWARE",
              "KENTUCKY",
              "WYOMING",
              "INDIANA",
              "NEW HAMPSHIRE",
              "ILLINOIS",
              "MISSISSIPPI",
              "NEW YORK",
              "NEBRASKA",
              "MAINE",
              "ARIZONA",
              "MINNESOTA",
              "ARKANSAS",
              "NORTH DAKOTA",
              "DISTRICT OF COLUMBIA",
              "MARYLAND",
              "VERMONT",
              "NEW MEXICO",
              "SOUTH CAROLINA",
              "MASSACHUSETTS",
              "IOWA",
              "RHODE ISLAND",
              "CONNECTICUT",
              "GEORGIA",
              "COLORADO",
              "SOUTH DAKOTA",
              "TENNESSEE",
              "KANSAS",
              "VIRGINIA",
              "ALABAMA",
              "OKLAHOMA",
              "FLORIDA",
              "TEXAS",
              "MONTANA",
              "UTAH",
              "MISSOURI",
              "CALIFORNIA",
              "IDAHO",
              "NORTH CAROLINA",
              "WEST VIRGINIA",
              "OREGON",
              "LOUISIANA",
              "PENNSYLVANIA",
              "PUERTO RICO",
              "ALASKA",
              "HAWAII",
              "GUAM",
              "VIRGIN ISLANDS, U.S.",
              "AMERICAN SAMOA",
              "NORTHERN MARIANA ISLANDS"]

    # for i in range(1940, 2020, 10):
    #     a = datetime.date(i, 1, 1)
    #     b = datetime.date(i + 9, 12, 31)
    #     print('(\'' + a.__str__() + '\'' + ', \'' + b.__str__() + '\')')

    date_ranges = [('1940-01-01', '1949-12-31'),
                   ('1950-01-01', '1959-12-31'),
                   ('1960-01-01', '1969-12-31'),
                   ('1970-01-01', '1979-12-31'),
                   ('1980-01-01', '1989-12-31'),
                   ('1990-01-01', '1999-12-31'),
                   ('2000-01-01', '2009-12-31'),
                   ('2010-01-01', '2019-12-31')]

    decades = [1880, 1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010]

    data_dictionary_list = []
    # print(values)

    for state in states:
        for decade in decades:
            data_dictionary = {}
            data_dictionary['State'] = state
            data_dictionary['Decade'] = decade
            for value in diseases:
                data_dictionary[value] = 0
            data_dictionary_list.append(data_dictionary)

    with open('cluster_data.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            if not row:
                continue
            for data_dictionary in data_dictionary_list:
                date_boolean = data_dictionary['Decade'] <= int(row[1]) <= data_dictionary['Decade'] + 9
                if data_dictionary['State'] == row[0] and date_boolean:
                    data_dictionary[row[2]] += int(float(row[3]))
                    print(data_dictionary)
    print("omg")
    with open('realer_cluster_data.csv', mode='w') as csv_file:
        fieldnames = ['State', 'Decade'] + diseases
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(data_dictionary_list)
    print("hmmm")

    count_query = """
    SELECT COALESCE(sum(CountValue), 0)
    FROM tycho.noncumulative_all_conditions
    WHERE Admin1Name = %s
    AND ConditionName = %s
    AND PeriodEndDate BETWEEN %s AND %s;
    """

    for state in states:
        data_row = list()
        data_row.append(state)
        for index, date_range in enumerate(date_ranges):
            data_row.append(decades[index])
            for disease in diseases:
                cursor = db_connection.cursor()
                parameters = (state, disease, date_range[0], date_range[1])
                cursor.execute(count_query, parameters)
                count = cursor.fetchone()[0]
                data_row.append(count)
        with open('cluster_data.csv', mode='a') as data_file:
            csv_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            csv_writer.writerow(data_row)
            print(data_row)


main()
