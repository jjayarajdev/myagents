from agents_store.db_agent.database.database_factory import DatabaseFactory
import logging

logger = logging.getLogger(__name__)

def db_query_exec(sql_query: str,db_type) -> str:
    """
    Execute a SQL query on the specified database type.

    Args:
        sql_query (str): The SQL query to be executed.
        db_type (str): The type of the database (e.g., 'snowflake_agent', 'postgres_agent').

    Returns:
        str: The result of the executed query.

    Raises:
        ValueError: If the SQL query is empty or the database type is unsupported.
    """
    db_operation = DatabaseFactory.get_database_operation(db_type)
    if sql_query:
       sql_query=db_operation.clean_query(sql_query)
       query_result = db_operation.execute_query(sql_query)
    return query_result