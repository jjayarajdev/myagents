# -----------------------------------------------------------------------------
# SECTION: Dynamic Import Functions
# -----------------------------------------------------------------------------

import importlib
import logging
import os
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

def dynamic_import(module_path: str) -> Any:
    """
    Dynamically imports a module from a string path.
    
    Args:
        module_path (str): Dot-separated path to the module to import
        
    Returns:
        The imported module or None if import fails
    """
    try:
        print(module_path)
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.warning(f"Could not import {module_path}: {e}")
        return None

def get_function_from_module(module_path: str, function_name: str) -> Optional[Callable]:
    """
    Dynamically imports a specific function from a module.
    
    Args:
        module_path (str): Dot-separated path to the module
        function_name (str): Name of the function to import
        
    Returns:
        The imported function or None if import fails
    """
    module = dynamic_import(module_path)
    if module and hasattr(module, function_name):
        return getattr(module, function_name)
    return None

def lazy_import_db_dependencies() -> Dict[str, Any]:
    """
    Lazily imports all DB-related dependencies and returns them in a dictionary.
    
    Returns:
        Dict containing all successfully imported DB modules and functions
    """
    db_deps = {}
    
    # Try to import get_dboconfig
    get_dboconfig_func = get_function_from_module("agents_store.db_agent.utils.helper_db_functions", "get_dboconfig")
    if get_dboconfig_func:
        db_deps["get_dboconfig"] = get_dboconfig_func
    
    # Try to import Queries
    queries_module = dynamic_import("agents_store.db_agent.utils.query_repository")
    if queries_module and hasattr(queries_module, "Queries"):
        db_deps["Queries"] = queries_module.Queries
    
    # Try to import db_query_prompt_loader
    db_query_prompt_loader_func = get_function_from_module(
        "agents_store.db_agent.func_executable.db_query_prompt_loader", "db_query_prompt_loader"
    )
    if db_query_prompt_loader_func:
        db_deps["db_query_prompt_loader"] = db_query_prompt_loader_func
    
    # Try to import db_query_exec
    db_query_exec_func = get_function_from_module("agents_store.db_agent.utils.db_agent_utils", "db_query_exec")
    if db_query_exec_func:
        db_deps["db_query_exec"] = db_query_exec_func
    
    return db_deps

def check_db_dependencies(required_deps: list) -> bool:
    """
    Checks if all required DB dependencies are available.
    
    Args:
        required_deps (list): List of dependency names to check
        
    Returns:
        True if all dependencies are available, False otherwise
    """
    db_deps = lazy_import_db_dependencies()
    return all(dep in db_deps for dep in required_deps)

# Add this to your generic_agent function
def get_dboconfig_safe(function_name: str) -> Optional[str]:
    """
    Safely attempts to get DB configuration, returning None if not available.
    
    Args:
        function_name (str): Name of the function to get configuration for
        
    Returns:
        DB configuration or None if not available
    """
    db_deps = lazy_import_db_dependencies()
    get_dboconfig_func = db_deps.get("get_dboconfig")
    
    if get_dboconfig_func:
        try:
            return get_dboconfig_func(function_name)
        except Exception as e:
            logger.warning(f"Error getting DB config: {e}")
    
    return None

def load_db_prompts(func_params: dict, db_deps: Dict[str, Any]) -> Tuple[str, str, str, int, int]:
    """
    Loads DB-specific prompts using the db_query_prompt_loader.
    
    Args:
        func_params (dict): Parameters for the prompt loader
        db_deps (Dict[str, Any]): Dictionary of DB dependencies
        
    Returns:
        Tuple of (system_text, example_text, schema_text, input_tokens_count, output_tokens_count)
    """
    db_query_prompt_loader = db_deps.get("db_query_prompt_loader")
    if not db_query_prompt_loader:
        raise ImportError("db_query_prompt_loader not available")
    
    return db_query_prompt_loader(func_params)

def execute_db_query(query: str, function_name: str, db_deps: Dict[str, Any]) -> Any:
    """
    Executes a DB query using the db_query_exec function.
    
    Args:
        query (str): Query to execute
        function_name (str): Name of the function
        db_deps (Dict[str, Any]): Dictionary of DB dependencies
        
    Returns:
        Query results
    """
    db_query_exec = db_deps.get("db_query_exec")
    if not db_query_exec:
        raise ImportError("db_query_exec not available")
    
    return db_query_exec(query, function_name)

def add_query_to_repository(query: str, db_deps: Dict[str, Any]) -> None:
    """
    Adds a query to the query repository.
    
    Args:
        query (str): Query to add
        db_deps (Dict[str, Any]): Dictionary of DB dependencies
    """
    Queries = db_deps.get("Queries")
    if Queries and hasattr(Queries, "query"):
        try:
            Queries.query.append(query)
        except Exception as e:
            logger.warning(f"Error adding query to repository: {e}")