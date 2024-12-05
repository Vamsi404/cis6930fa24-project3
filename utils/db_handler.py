import sqlite3

def create_database():
    # Specify the path to your database file
    connection = sqlite3.connect('./resources/normanpd.db')
    
    # Create table for storing incident data if it doesn't already exist
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY,
                incident_type TEXT,
                incident_time TEXT,
                location TEXT,
                description TEXT
            )
        """)
    return connection

def populate_database(connection, incidents):
    with connection:
        for incident in incidents:
            connection.execute("""
                INSERT INTO incidents (incident_type, incident_time, location, description)
                VALUES (?, ?, ?, ?)
            """, (incident['incident_type'], incident['incident_time'], incident['location'], incident['description']))

def fetch_incident_summary(connection):
    # Query the database to get a summary of incidents
    cursor = connection.cursor()
    cursor.execute("""
        SELECT incident_type, COUNT(*) as count
        FROM incidents
        GROUP BY incident_type
    """)
    summary = cursor.fetchall()
    return [{"incident_type": row[0], "count": row[1]} for row in summary]
