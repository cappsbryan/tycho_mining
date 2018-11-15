"""
Run this script to initialize your database for the project

First, install MySQL server on your machine.
    Go download it and go through that process.
    Create a database named tycho and a user named tycho_dev with a password dev123
    The following MySQL commands should work for this:
        create database tycho;
        create user 'tycho_dev'@'localhost' identified by 'dev123';
        grant all on tycho.* to 'tycho_dev'@'localhost';

Second, make sure you have installed the libraries in the requirements.txt
    Pycharm should show a banner at the top to do that.

Third, make sure you download and copy the CSV files into a csv folder inside this setup folder.
    They should be named cumulative all conditions weekly US.csv and noncumulative all conditions weekly US.csv

Fourth, run this script.
    On my computer it takes about an hour to insert every row in both CSVs into the database.
"""
import csv
import os

from datetime import datetime
from typing import List, Union

import MySQLdb

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)

setup_dir = os.path.dirname(os.path.abspath(__file__))

csv_file = None


def main():
    if tables_exist():
        return
    create_tables()
    cumulative_path = os.path.join(setup_dir, 'csv', 'cumulative all conditions weekly US.csv')
    noncumulative_path = os.path.join(setup_dir, 'csv', 'noncumulative all conditions weekly US.csv')
    save_data(cumulative_path, cumulative_insert_statement())
    save_data(noncumulative_path, noncumulative_insert_statement())
    db_connection.close()
    csv_file.close()


def tables_exist() -> bool:
    """
    Returns true if EITHER table exists
    """
    check_cumulative = "SELECT count(*) FROM information_schema.TABLES " \
                       "WHERE (TABLE_SCHEMA = 'tycho') AND (TABLE_NAME = 'cumulative_all_conditions')"
    check_noncumulative = "SELECT count(*) FROM information_schema.TABLES " \
                          "WHERE (TABLE_SCHEMA = 'tycho') AND (TABLE_NAME = 'noncumulative_all_conditions')"
    cursor = db_connection.cursor()
    cursor.execute(check_cumulative)
    cumulative_exists = cursor.fetchone()
    cursor.execute(check_noncumulative)
    noncumulative_exists = cursor.fetchone()
    # fetchone returns a tuple, in this case with one element 1 or 0
    return cumulative_exists[0] == 1 or noncumulative_exists[0] == 1


def create_tables():
    cursor = db_connection.cursor()
    sql_path = os.path.join(setup_dir, "create_tables.sql")
    with open(sql_path, 'rt') as sql_file:
        sql_file_string = sql_file.read()
        commands = sql_file_string.split(';')
        commands = commands[:-1]  # ignore the whitespace after the last statement
        for command in commands:
            try:
                cursor.execute(command)
            except MySQLdb.OperationalError as msg:
                print("Command failed:", msg)
                print("Exiting program")
                exit(1)


def save_data(path, insert_statement: str):
    global csv_file
    csv_file = open(path, newline='')
    rows = csv.reader(csv_file)
    cursor = db_connection.cursor()
    header = rows.__next__()
    age_range_index = replace_age_range_label(header)
    i = 0
    for row in rows:
        replace_age_range(row, age_range_index)
        replace_na(row)
        if i % 500 == 0:
            db_connection.commit()
            print(i, datetime.now(), insert_statement, row)
        cursor.execute(insert_statement, row)
        i += 1
    # cursor.executemany(insert_statement, rows)
    # replace insert_many call below with executemany call above if you don't care about progress updates
    insert_many(cursor, insert_statement, rows)
    cursor.close()
    db_connection.commit()


def insert_many(cursor, insert_statement, rows):
    """
    Inserts many rows with the given cursor and insert statement
    :param cursor: Database cursor
    :param insert_statement: Insert statement with placeholders
    :param rows: List of placeholder lists
    """
    i = 0
    for row in rows:
        if i % 500 == 0:
            db_connection.commit()
            print(i, datetime.now(), insert_statement, row)
        cursor.execute(insert_statement, row)
        i += 1


def replace_age_range_label(header):
    """
    The CSV files contain a field called AgeRange,
    but we split the range into two separate fields when storing in the DB
    :param header: The list of fields at the top of the CSV file
    :return: The index of the AgeRangeStart field
    """
    index = header.index('AgeRange')
    header[index] = 'AgeRangeStart'
    header.insert(index + 1, 'AgeRangeEnd')
    return index


def cumulative_insert_statement():
    return f"INSERT cumulative_all_conditions ({column_names()}) VALUES ({placeholders()});"


def noncumulative_insert_statement():
    return f"INSERT noncumulative_all_conditions ({column_names()}) VALUES ({placeholders()});"


def column_names():
    return "ConditionName, " \
           "ConditionSNOMED, PathogenName, PathogenTaxonID, Fatalities, " \
           "CountryName, CountryISO, Admin1Name, Admin1ISO, Admin2Name, " \
           "CityName, PeriodStartDate, PeriodEndDate, " \
           "PartOfCumulativeCountSeries, AgeRangeStart, AgeRangeEnd, " \
           "Subpopulation, PlaceOfAquisition, DiagnosisCertainty, " \
           "SourceName, CountValue, DOI"


def placeholders():
    return "%s, " * 21 + "%s"


def replace_age_range(row, age_range_index):
    """
    Replaces the age range value in this row with two values for the start and end of the range
    :param row: The row to change
    :param age_range_index: The index of the age range value in the row
    :return: None, replaces the row in-place
    """
    age_range = row[age_range_index].split('-')
    row[age_range_index] = age_range[0]
    row.insert(age_range_index + 1, age_range[1])


def replace_na(row: List[Union[str, None]]):
    """
    Replace any NA values in the CSV with the Python value None
    :param row: A single row from a CSV file
    """
    for i, value in enumerate(row):
        if value == 'NA':
            row[i] = None


if __name__ == '__main__':
    main()
