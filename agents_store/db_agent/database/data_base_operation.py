import re
from typing import Any
import logging

logger = logging.getLogger(__name__)
class DatabaseOperation:
    def clean_query(self, query: str) -> str:
        """
        Clean unwanted double quotes from a SQL query while keeping
        double quotes around identifiers with special characters.
        """
        cleaned_query = re.sub(r'\"([a-zA-Z0-9_]+)\"', r'\1', query)
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query)
        logger.info(f"Cleaned query: {cleaned_query}")
        return cleaned_query.strip()

    def execute_query(self, sql_query: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")


