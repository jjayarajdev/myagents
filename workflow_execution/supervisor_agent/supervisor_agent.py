"""
Module Name: supervisor_agent.py

Description:
This module contains the implementation of the Supervisor agent using LangChain components.
The Supervisor agent is responsible for analyzing user input and generating a structured response that 
includes tasks, corresponding function calls, and dependencies between tasks.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import os
from typing import List, Optional
import json
from pathlib import Path

# Third-party imports
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Local application imports
from models.openai.azure_openai_model import llm_config_loader
from utils.helper_functions import load_prompt_yaml,find_directory,load_functions_prompt,get_required_agents

# -----------------------------------------------------------------------------
# SECTION: Load Prompts
# -----------------------------------------------------------------------------




# -----------------------------------------------------------------------------
# SECTION: Define Models and Chain
# -----------------------------------------------------------------------------

class QuestionIntent(BaseModel):
    """
    Pydantic model for a question intent.

    Attributes:
        question (str): User's question or request.
        function_name (str): Function name to be called based on user input.
        function_params (List[str]): List of function parameters.
        depends_on (Optional[int]): Index of the question this depends on, if any.
    """
    question: str = Field(description="User's question or request")
    function_name: str = Field(description="Function name to be called based on user input")
    function_params: List[str] = Field(description="List of function parameters")
    depends_on: Optional[int] = Field(None, description="Index of the question this depends on, if any")


class Supervisor(BaseModel):
    """
    Pydantic model for the supervisor's response.

    Attributes:
        tasks (List[QuestionIntent]): List of questions and their corresponding function names, 
        params, and dependencies.
    """
    tasks: List[QuestionIntent] = Field(description="List of questions and their corresponding function names, params, and dependencies")






def loading_prompt_files(user):


    user_dir_path = os.path.join(os.getcwd(),'user_config_files',user,'supervisor_agent_prompts')
    required_agents = get_required_agents(user)
    print(required_agents)
    # Load prompts from files
    directory = find_directory(Path.cwd(),'supervisor_prompts')
    directory = r"{}".format(directory)
    supervisor_system_text = load_prompt_yaml(directory+ r"\system_prompt.yaml")
    supervisor_functions_text = load_functions_prompt(required_agents)
    supervisor_schema_text = load_prompt_yaml(directory+ r"\schema_prompt.yaml")
    if Path(user_dir_path+ r"\example_prompt.yaml").exists():
        supervisor_example_text = load_prompt_yaml(user_dir_path+ r"\example_prompt.yaml")
    else:
        supervisor_example_text = load_prompt_yaml(directory+ r"\example_prompt.yaml")
    supervisor_start_text = load_prompt_yaml(directory + r"\start_prompt.yaml")


    # Create chat prompt templates from the loaded prompts
    system_supervisor_prompt = ChatPromptTemplate.from_template(supervisor_system_text)
    system_functions_supervisor_prompt = ChatPromptTemplate.from_template(supervisor_functions_text)
    schema_supervisor_prompt = ChatPromptTemplate.from_template(supervisor_functions_text)
    example_supervisor_prompt = ChatPromptTemplate.from_template(supervisor_example_text)
    start_supervisor_prompt = ChatPromptTemplate.from_template(supervisor_start_text)

    # -----------------------------------------------------------------------------
    # SECTION: Define and Create Prompt Template
    # -----------------------------------------------------------------------------

    # Define a standard template for the prompts
    standard_template = """
    ## System: {system}
    ## functions: {functions}
    ## Example: {example}
    ## Start: {start}
    """
    standard_template = PromptTemplate.from_template(standard_template)

    # Define the conversation template as a list of tuples
    conversation_template = [
        ("system", system_supervisor_prompt),
        ("functions", system_functions_supervisor_prompt),
        ("example", example_supervisor_prompt),
        ("start", start_supervisor_prompt)
    ]
    # Create a pipeline prompt template for the Ask Ellis Supervisor agent
    supervisor_prompt = PipelinePromptTemplate(
        final_prompt=standard_template,
        pipeline_prompts=conversation_template
    )
    # Create the output parser
    parser = JsonOutputParser(pydantic_object=Supervisor)

    # Create the supervisor chain by combining the prompt, model, and parser
    supervisor_chain = supervisor_prompt | llm_config_loader() | parser

    return supervisor_chain


# -----------------------------------------------------------------------------
# SECTION: Supervisor Agent Function
# -----------------------------------------------------------------------------

def supervisor_agent(user_name: str, user_country: str, full_user_details, user_input: str, conversation_history: list, retry_context: list,user) -> tuple:
    """
    Generate a supervisor response based on the user input.

    This function processes the user's input, generates a structured response using the 
    Supervisor agent chain, and returns the response along with token usage statistics.

    Args:
        user_name (str): The name of the user initiating the query.
        user_input (str): The user's input question or request.
        conversation_history (list): The conversation history leading up to the current input.

    Returns:
        tuple: A tuple containing:
            - dict: The AI-generated supervisor response.
            - int: The number of input tokens used.
            - int: The number of output tokens generated.
    """
    supervisor_chain = loading_prompt_files(user)
    with get_openai_callback() as cb:
        ai_response = supervisor_chain.invoke({
            "user_name": user_name,
            "user_country": user_country,
            "full_user_details": json.dumps(full_user_details),
            "user_input": user_input,
            "conversation_history": conversation_history,
            "retry_context": retry_context
        })
    print("AI Response Supervisor Agent: ", ai_response)
    input_tokens_count = cb.prompt_tokens
    output_tokens_count = cb.completion_tokens
    return ai_response, input_tokens_count, output_tokens_count

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------