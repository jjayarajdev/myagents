import hashlib
from access_controller.database import DatabaseConnection

class UserManagement:
    def __init__(self, db_connection):
        """
        Initialize the UserManagement class.

        Args:
            db_connection (DatabaseConnection): The database connection to use.
        """
        self.db_connection = db_connection
    
    def create_user(self, email, password, name):
        """
        Create a new user.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
            name (str): The name of the user.

        Returns:
            int or None: The ID of the newly created user, or None if the creation failed.
        """
        query = "INSERT INTO users (email, password, name) VALUES (%s, %s, %s) RETURNING id"
        params = (email, password, name)
        result = self.db_connection.execute_query(query, params)
        if result and result[0]:
            return result[0][0]
        else:
            return None


    def assign_folder_access(self, user_id, files_path):
        """
        Assign folder access to a user.

        Args:
            user_id (int): The ID of the user.
            files_path (str): The path to the folder.

        Returns:
            bool: True if the folder access is assigned successfully, False otherwise.
        """
        query = "INSERT INTO folder_access (user_id, files_path) VALUES (%s, %s)"
        params = (user_id, files_path)
        result = self.db_connection.execute_query(query, params)
        return result is not None

    def get_user_folders(self, user_id):
        """
        Get a list of folders assigned to a user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            list: The list of folders assigned to the user.
        """
        query = "SELECT files_path FROM folder_access WHERE user_id = %s"
        params = (user_id,)
        result = self.db_connection.execute_query(query, params)
        return result
    
    def verify_user(self, email, password):
        """
        Verify a user's email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.

        Returns:
            int or None: The ID of the user if the email and password are correct, or None if they are not.
        """
        query = "SELECT id FROM users WHERE email = %s AND password = %s"
        params = (email, password)
        result = self.db_connection.execute_query(query, params)
        if result and result[0]:
            return True
        else:
            return False
    
    def get_user_id_by_email(self, email):
        """
        Get the ID of a user based on their email.

        Args:
            email (str): The email address of the user.

        Returns:
            int or None: The ID of the user if the email is found, or None if it is not.
        """
        query = "SELECT id FROM users WHERE email = %s"
        params = (email,)
        result = self.db_connection.execute_query(query, params)
        if result and result[0]:
            return result[0][0]
        else:
            return None
    
    
    def create_tables(self):
        query = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS folder_access (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                files_path VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """
        return self.db_connection.execute_query(query)