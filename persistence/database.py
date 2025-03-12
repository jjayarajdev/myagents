import psycopg2
import os
import logging
 
from dotenv import load_dotenv
 
# Get a logger instance for this module
logger = logging.getLogger(__name__)
 
load_dotenv()
 
# Retrieve environment variables
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")
POSTGRES_USERNAME = os.getenv("POSTGRES_USERNAME")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
 
 
class DatabaseConnection:
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
 
    def establish_connection(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            logger.info("Connection established successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to establish connection: {e}")
            raise e
 
    def close_connection(self):
        try:
            self.conn.close()
            logger.info("Connection closed successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to close connection: {e}")
            raise e
 
    def execute_query(self, query, params=None):
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            self.conn.commit()
            logger.info("Query executed successfully")
        except psycopg2.Error as e:
            logger.error(f"Failed to execute query: {e}")
            raise e
 
    def fetch_data(self, query, params=None):
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(query, params)
            else:
                cur.execute(query)
            rows = cur.fetchall()
            return rows
        except psycopg2.Error as e:
            logger.error(f"Failed to fetch data: {e}")
            raise e