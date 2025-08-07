import mysql.connector
import configparser
import logging

class MySQLHandler:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.conn = mysql.connector.connect(
            host=config['mysql']['host'],
            user=config['mysql']['user'],
            password=config['mysql']['password'],
            database=config['mysql']['database']
        )
        self.cursor = self.conn.cursor()
        logging.info("Connected to MySQL database")

    def create_tables(self):
        try:
            with open('sql/create_tables.sql', 'r') as f:
                sql_script = f.read()
                for statement in sql_script.strip().split(';'):
                    if statement.strip():
                        self.cursor.execute(statement)
            self.conn.commit()
            logging.info(" Tables created successfully")
        except Exception as e:
            logging.error(f"Failed to create tables: {e}")

    def insert_data(self, table_name, data):
        """
        Insert data into the specified table.
        """
        query = f"""
        INSERT IGNORE INTO {table_name} (country, date, cases, deaths, recovered)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.cursor.executemany(query, data)
            self.conn.commit()
            logging.info(f" Inserted {self.cursor.rowcount} records into {table_name}")
        except mysql.connector.Error as err:
            logging.error(f" Error inserting data: {err}")
            self.conn.rollback()

    def list_tables(self):
        try:
            self.cursor.execute("SHOW TABLES")
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f" Failed to list tables: {err}")
            return []

    def query(self, query, params=None):
        """
        Execute a SELECT query and return results.
        """
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            logging.error(f" Query execution failed: {err}")
            return []

    def close(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            logging.info(" MySQL connection closed")
