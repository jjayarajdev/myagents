from access_controller.database import DatabaseConnection
from access_controller.user_management import UserManagement
import json

class AccessHandler:
    """
    This class handles access control functionality, including user management and folder access.
    """

    def __init__(self):
        """
        Initializes the AccessHandler class by establishing a connection to the database.
        """
        self.db_connection = None
        self.user_management = None
        # Establish a connection to the database when the class is initialized
        self.establish_connection()

    def establish_connection(self):
        """
        Establishes a connection to the database.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        # Create a new DatabaseConnection object
        self.db_connection = DatabaseConnection()
        # Attempt to establish a connection to the database
        if self.db_connection.establish_connection():
            # Create a new UserManagement object with the established database connection
            self.user_management = UserManagement(self.db_connection)
            return True
        else:
            print("Failed to establish database connection.")
            return False

    def create_user(self, email, password, name):
        """
        Creates a new user with the given email, password, and name.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.
            name (str): The name of the user.

        Returns:
            str: A JSON response indicating whether the user was created successfully.
        """
        # Use the UserManagement object to create a new user
        results = self.user_management.create_user(email, password, name)
        # Check if the user was created successfully
        if results is not None:
            # Return a JSON response indicating success
            resp = json.dumps({"status": "success", "user_id": results})
        else:
            # Return a JSON response indicating failure
            resp =  json.dumps({"status": "failed", "error": "Failed to create user"})
        return resp

    def assign_folder_access(self, user_id, files_path):
        """
        Assigns folder access to a user with the given user ID and files path.

        Args:
            user_id (int): The ID of the user.
            files_path (str): The path to the files.

        Returns:
            str: A JSON response indicating whether the folder access was assigned successfully.
        """
        # Use the UserManagement object to assign folder access
        results = self.user_management.assign_folder_access(user_id, files_path)
        # Check if the folder access was assigned successfully
        if results:
            # Return a JSON response indicating success
            resp  = json.dumps({"status": "success", "message": "Folder access assigned successfully"})
        else:
            # Return a JSON response indicating failure
            resp = json.dumps({"status": "failed", "error": "Failed to assign folder access"})
        return resp

    def get_user_folders(self, user_id):
        """
        Retrieves the folders assigned to a user with the given user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: A JSON response containing the folders assigned to the user.
        """
        # Use the UserManagement object to retrieve the user's folders
        results = self.user_management.get_user_folders(user_id)
        # Check if the user has any folders
        if results is not None and len(results) > 0:
            # Return a JSON response containing the folders
            resp  = json.dumps({"status": "success", "folders": results})
        else:
            # Return a JSON response indicating that no folders were found
            resp = json.dumps({"status": "failed", "error": "No folders found for user"})
        return resp

    def verify_user(self, email, password):
        """
        Verifies a user's email and password.

        Args:
            email (str): The email address of the user.
            password (str): The password of the user.

        Returns:
            str: A JSON response indicating whether the user's credentials are valid.
        """
        # Use the UserManagement object to verify the user's credentials
        results = self.user_management.verify_user(email, password)
        # Check if the user's credentials are valid
        if results:
            # Return a JSON response indicating success
            resp = json.dumps({"status": "success", "user_id": results})
        else:
            # Return a JSON response indicating failure
            resp = json.dumps({"status": "failed", "error": "Invalid email or password"})
        return resp
    
    def get_user_id_by_email(self, email):
        """
        Gets the ID of a user based on their email.

        Args:
            email (str): The email address of the user.

        Returns:
            str: A JSON response containing the user's ID.
        """
        # Use the UserManagement object to get the user's ID
        results = self.user_management.get_user_id_by_email(email)
        # Check if the user's ID was found
        if results:
            # Return a JSON response containing the user's ID
            resp = json.dumps({"status": "success", "user_id": results})
        else:
            # Return a JSON response indicating that the user was not found
            resp = json.dumps({"status": "failed", "error": "User not found"})
        return resp

    def close_connection(self):
        """
        Closes the connection to the database.
        """
        # Check if a database connection exists
        if self.db_connection:
            # Close the database connection
            self.db_connection.close_connection()
    
    def execute(self, data):
        required_fields = {
            "registration": ["email", "password", "name"],
            "addfolderaccess": ["user_id", "files_path"],
            "getfolderaccessdetails": ["user_id"],
            "verifyuser": ["email", "password"],
            "getuserid": ["email"]
        }

        func_name = data.get("func_name")
        
        if func_name not in required_fields:
            return {"error": "invalid func_name", "status": "failed"}

        required_fields_for_func = required_fields[func_name]
        if not all(field in data for field in required_fields_for_func):
            return {"error": f"required fields for {func_name} are: {', '.join(required_fields_for_func)}", "status": "failed"}

        match func_name:
            case "registration":
                return self.create_user(data.get("email"), data.get("password"), data.get("name"))
            case "addfolderaccess":
                return self.assign_folder_access(data.get("user_id"), data.get("files_path"))
            case "getfolderaccessdetails":
                return self.get_user_folders(data.get("user_id"))
            case "verifyuser":
                return self.verify_user(data.get("email"), data.get("password"))
            case "getuserid":
                return self.get_user_id_by_email(data.get("email"))