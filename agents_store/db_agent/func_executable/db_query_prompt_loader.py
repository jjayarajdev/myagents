import os
import yaml
import logging
from pathlib import Path

from agents_store.db_agent.func_executable.db_table_pruning_agent import db_table_pruning_agent
from agents_store.db_agent.utils.helper_functions import load_prompt_yaml


logger = logging.getLogger(__name__)


# dir_path = os.path.join(os.getcwd(),r"agents_store\db_agent\config_files\db_agent_prompts")
templates_path=Path(os.path.join(os.getcwd(),r"agents_store\db_agent\config_files\db_agent_prompts\general_guidelines"))

def load_db_prompt_text(table_names,file_name,user):
    """
    Load the database prompt text from YAML files for the given table names.

    Args:
        table_names (List[str]): List of table names to load prompts for.
        file_name (str): The name of the YAML file containing the prompts.

    Returns:
        str: The concatenated prompt text for all specified tables.
    """
    logger.info(f"Loading database prompt text for tables: {table_names} from file: {file_name}")
    dir_path = os.path.join(os.getcwd(),'user_config_files',user,'db_agent_prompts')
    file_path = os.path.join(dir_path,file_name)
    prompt_text =load_template_yaml(file_name)
    for table_name in table_names:
        file_path = os.path.join(dir_path, table_name, file_name)
        print(file_path)
        prompt_content = load_prompt_yaml(file_path)
        prompt_text += f"\n{table_name}:\n{prompt_content}"
    return prompt_text

def load_template_yaml(file_name):
    """
    Load the template YAML file content.

    Args:
        file_name (str): The name of the YAML file to load.

    Returns:
        str: The content of the YAML file.
    """
    file_path = os.path.join(templates_path, file_name)
    prompt_text = load_prompt_yaml(file_path)
    return prompt_text

def db_query_prompt_loader(func_params,user):
    # Use the db_table_pruning_agent to get the table names and token counts
    table_names, input_tokens_count, output_tokens_count = db_table_pruning_agent(func_params,user)
    
    # Convert all table names to lowercase
    table_names = [name.lower() for name in table_names]
    
    print("*" * 50)
    print("Agent selected table names")
    print(table_names)
    print("*" * 50)

    # Load dynamic example prompts based on identified table names for query generation
    db_query_generation_system_text = load_db_prompt_text(table_names, 'system_prompt.yaml',user)
    db_query_generation_schema_text = load_db_prompt_text(table_names, 'schema_prompt.yaml',user)
    db_query_generation_example_text = load_db_prompt_text(table_names, 'example_prompt.yaml',user)
    
    # Return the loaded prompt texts and token counts
    return db_query_generation_system_text, db_query_generation_schema_text, db_query_generation_example_text, input_tokens_count, output_tokens_count
