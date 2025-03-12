from typing import Dict, Any
import logging
import json
import psycopg2

from agents_store.db_agent.database.data_base_operation import DatabaseOperation
# Third-party imports
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# SECTION: Logger Setup
# -----------------------------------------------------------------------------

# Get a logger instance for this module
logger = logging.getLogger(__name__)

class postgresOperation(DatabaseOperation):
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params

    def execute_query(self, sql_query: str) -> str:
        """
        Execute a SQL query on Snowflake and return the result as a JSON string.
        """
        conn = None
        cur = None

        try:
            # Establish a connection to Snowflake
            conn = psycopg2.connect(**self.connection_params)
            # Create a cursor object
            cur = conn.cursor()

            # Execute the query and fetch the results
            cur.execute(self.clean_query(sql_query))
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            records = [dict(zip(columns, row)) for row in rows]
           
            # Convert the results to JSON format
            json_data = json.dumps(records, indent=4)
            return json_data

        except psycopg2.Error as e:
            # print(f"Error: {e}")
            logger.error(e)
            return None

        finally:
            # Close the cursor and connection
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()


