import json
import snowflake.connector
from typing import Dict, Any

from agents_store.db_agent.database.data_base_operation import DatabaseOperation

import logging


logger = logging.getLogger(__name__)

class SnowflakeOperation(DatabaseOperation):
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
            conn = snowflake.connector.connect(**self.connection_params)

            # Create a cursor object
            cur = conn.cursor()
            
            # Execute the query and fetch the results
            cur.execute(sql_query)
            column_names = [metadata.name for metadata in cur.description]
            rows = cur.fetchall()

            # Convert the results to JSON format
            json_data = json.dumps([
                {key: str(value) for key, value in zip(column_names, row)}
                for row in rows
            ])
            return json_data

        except snowflake.connector.errors.ProgrammingError as pe:
            logger.error(pe)
            return json.dumps({"error": str(pe)})

        except snowflake.connector.errors.DatabaseError as de:
            logger.error(de)
            return json.dumps({"error": f"Snowflake Database Error: {de}"})

        except Exception as e:
            logger.error(e)
            return json.dumps({"error": f"An unexpected error occurred: {e}"})

        finally:
            # Ensure the cursor is closed
            if cur:
                try:
                    cur.close()
                except Exception:
                    pass

            # Ensure the connection is closed
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
