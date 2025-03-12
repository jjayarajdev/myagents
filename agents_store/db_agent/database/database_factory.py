# src/database/database_factory.py
from typing import Dict, Any
from agents_store.db_agent.database.snowflake_operation import SnowflakeOperation
from agents_store.db_agent.database.postgres_operation import postgresOperation  # Import PostgreSQL operation
from agents_store.db_agent.database.config import SnowflakeConfig, PostgresConfig
import logging

logger = logging.getLogger(__name__)


class DatabaseFactory:
    @staticmethod
    def get_database_operation(db_type: str):
        """
            
        Get the database operation instance based on the database type.

        Args:
            db_type (str): The type of the database (e.g., 'snowflake_agent', 'postgres_agent').

        Returns:
            An instance of the corresponding database operation class.

        Raises:
            ValueError: If the provided database type is unsupported.
         
        """
        logger.info(f"Getting database operation for type: {db_type}")
        connection_params = DatabaseFactory.load_connection_params(db_type)
        if db_type == "snowflake_agent":
            return SnowflakeOperation(connection_params)
        elif db_type == "postgres_agent":
            return postgresOperation(connection_params) 
        else:
            logger.error(f"Unsupported database type: {db_type}")
            raise ValueError("Unsupported database type")
        
    @staticmethod
    def load_connection_params(db_type: str) -> Dict[str, Any]:
        """
        Load the connection parameters for the specified database type.

        Args:
            db_type (str): The type of the database.

        Returns:
            Dict[str, Any]: The connection parameters for the database.
        """
        logger.info(f"Loading connection parameters for database type: {db_type}")
        config_classes = {
            "snowflake_agent": SnowflakeConfig,
            "postgres_agent": PostgresConfig,
        }

        if db_type not in config_classes:
            logger.error(f"Unsupported database type for connection parameters: {db_type}")
            raise ValueError("Unsupported database type")

        return config_classes[db_type].load()