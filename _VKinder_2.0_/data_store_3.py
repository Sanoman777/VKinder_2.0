import psycopg2
from psycopg2 import sql

class DataStore:
    def __init__(self, db_url_object):
        self.conn = psycopg2.connect(db_url_object)
        self.cursor = self.conn.cursor()

    def create_table(self):
        create_table_query = """
            CREATE TABLE IF NOT EXISTS search_results (
                profile_id INTEGER,
                worksheet_id INTEGER
            )
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()

    def insert_result(self, profile_id, worksheet_id):
        insert_query = sql.SQL("INSERT INTO search_results (profile_id, worksheet_id) VALUES (%s, %s)")
        self.cursor.execute(insert_query, (profile_id, worksheet_id))
        self.conn.commit()

    def get_results(self):
        select_query = sql.SQL("SELECT profile_id, worksheet_id FROM search_results")
        self.cursor.execute(select_query)
        return self.cursor.fetchall()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
