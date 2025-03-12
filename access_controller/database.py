import psycopg2
from psycopg2 import Error
from access_controller.utils.config import DatabaseConfig

class DatabaseConnection:
    def __init__(self):
        """
        Initialize the DatabaseConnection class.
        """
        self.host_name = DatabaseConfig.POSTGRES_HOST
        self.db_name = DatabaseConfig.POSTGRES_DATABASE
        self.user_name = DatabaseConfig.POSTGRES_USERNAME
        self.user_password = DatabaseConfig.POSTGRES_PASSWORD
        self.connection = None

    def establish_connection(self):
        """
        Establish a connection to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.host_name,
                database=self.db_name,
                user=self.user_name,
                password=self.user_password
            )
            return True
        except Error as e:
            print(f"Error establishing connection: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """
        Execute a query on the database.

        Args:
            query (str): The query to execute.
            params (tuple, optional): The parameters to use in the query. Defaults to None.

        Returns:
            list or bool: The result of the query, or True if the query was an INSERT or UPDATE without RETURNING clause.
        """
        if not self.connection:
            print("No active database connection.")
            return []

        cursor = self.connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if query.upper().startswith("SELECT") or "RETURNING" in query.upper():
                result = cursor.fetchall()
                self.connection.commit()
                return result
            else:
                self.connection.commit()
                return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False

    def close_connection(self):
        """
        Close the database connection.
        """
        if self.connection:
            self.connection.close()