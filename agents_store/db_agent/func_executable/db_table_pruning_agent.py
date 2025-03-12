"""
Module Name: snowflake_table_identification_agent.py

Description:
This module identifies appropriate Snowflake table names based on user input
using an LLM-powered query chain. It loads prompts, defines models, and sets up
the necessary components to generate, parse, and execute Snowflake SQL queries.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import os
from typing import List

# Third-party imports
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Local application imports
from agents_store.db_agent.models.openai.azure_openai_model import llm_config_loader
from agents_store.db_agent.utils.helper_functions import load_prompt_yaml

import logging

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# SECTION: Define Models and Chain
# -----------------------------------------------------------------------------

class db_Table(BaseModel):
    """
    Pydantic model for parsing the response from Snowflake query execution.

    Attributes:
        table_names (List[str]): List of Snowflake table names identified from the query.
    """
    table_names: List[str] = Field(description="List of table names identified")


# -----------------------------------------------------------------------------
# SECTION: Load Prompts
# -----------------------------------------------------------------------------



def loading_prompt_files(user):
    user_dir_path = os.path.join(os.getcwd(),'user_config_files',user,'table_pruning_agent_prompts')
    template_dir_path=os.path.join(os.getcwd(),'agents_store','db_agent','config_files','table_pruning_agent_prompts')

    db_system_text = load_prompt_yaml(os.path.join(user_dir_path,'system_prompt.yaml'))
    db_start_text = load_prompt_yaml(os.path.join(template_dir_path,'start_prompt.yaml'))
    db_example_text = load_prompt_yaml(os.path.join(user_dir_path,'example_prompt.yaml'))

    # Create chat prompt templates from the loaded prompt texts
    system_db_prompt = ChatPromptTemplate.from_template(db_system_text)
    start_db_prompt = ChatPromptTemplate.from_template(db_start_text)
    example_db_prompt = ChatPromptTemplate.from_template(db_example_text)

    # -----------------------------------------------------------------------------
    # SECTION: Define and Create Prompt Template
    # -----------------------------------------------------------------------------

    # Define a standard template for system and start prompts
    standard_template = """
    ## System: {system}
    ## Start: {start}
    ## Example: {example}
    """
    standard_template = PromptTemplate.from_template(standard_template)

    # Define the snowflake template as a list of tuples containing the prompt types
    db_template = [
        ("system", system_db_prompt),
        ("start", start_db_prompt),
        ("example",example_db_prompt)
    ]

    # Create a pipeline prompt template for the Snowflake query chain
    db_table_pruning_prompt = PipelinePromptTemplate(
        final_prompt=standard_template,
        pipeline_prompts=db_template
    )
    # Create the output parser to handle JSON responses from the model
    parser = JsonOutputParser(pydantic_object=db_Table)

    # Create the complete Snowflake query chain by combining the prompt, model, and parser
    db_table_pruning_chain = db_table_pruning_prompt | llm_config_loader() | parser

    return db_table_pruning_chain

# -----------------------------------------------------------------------------
# SECTION: Snowflake Table Identification Agent Function
# -----------------------------------------------------------------------------

def db_table_pruning_agent(input_text: str,user) -> tuple:
    """
    Generates appropriate Snowflake table names based on user input.

    This function processes the user's input text, generates a SQL query using the
    Snowflake query chain, executes the query, and returns the identified table names
    along with token counts.

    Args:
        input_text (str): The user input text for table identification.

    Returns:
        tuple: A tuple containing:
            - list: Identified table names.
            - int: Number of input tokens used.
            - int: Number of output tokens generated.
    """
    db_table_pruning_chain = loading_prompt_files(user)
    with get_openai_callback() as cb:
        ai_response = db_table_pruning_chain.invoke({"user_input": input_text})
        table_names = ai_response["ai_response"]["table_names"]
        input_tokens_count = cb.prompt_tokens
        output_tokens_count = cb.completion_tokens

    return table_names, input_tokens_count, output_tokens_count

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------