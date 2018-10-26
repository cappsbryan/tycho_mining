import MySQLdb

db_connection = MySQLdb.connect(
    host="localhost",
    user="tycho_dev",
    passwd="dev123",
    db="tycho"
)


def fatality_data():
    cursor = db_connection.cursor()
    cursor.execute("SELECT AVG(CountValue) FROM noncumulative_all_conditions WHERE Fatalities = 1;")
    average_fatalities = cursor.fetchone()[0]
    cursor.execute("SELECT MAX(CountValue) FROM noncumulative_all_conditions WHERE Fatalities = 1;")
    max_fatalities = cursor.fetchone()[0]
    cursor.execute("SELECT MIN(CountValue) FROM noncumulative_all_conditions WHERE Fatalities = 1;")
    min_fatalities = cursor.fetchone()[0]
    return average_fatalities, min_fatalities, max_fatalities
