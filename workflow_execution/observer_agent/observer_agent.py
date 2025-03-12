"""
Module Name: observer_agent.py

Description:
This module contains the implementation of the observer agent. 
The observer agent is responsible for validating the outputs of various agents and providing feedback for adjustments. 
It checks the correctness, relevance, and completeness of the outputs, identifies errors, and suggests improvements for further iterations.

The module defines the following functions:
- observer_agent: Validates the outputs of various agents and provides feedback for adjustments.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
from typing import Any, Dict, List, Tuple

# Third-party imports
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

# Local application imports
from models.openai.azure_openai_model import llm_config_loader
from utils.helper_functions import load_prompt_yaml

# -----------------------------------------------------------------------------
# SECTION: Load Prompt
# -----------------------------------------------------------------------------
 
# Load the observer agent system prompt from a file
observer_agent_system_text = load_prompt_yaml(r"workflow_execution\observer_agent\observer_agent_prompts\system_prompt.yaml")
 
# Create chat prompt template
observer_agent_prompt = ChatPromptTemplate.from_messages(
    [("system", observer_agent_system_text)]
)
 
# -----------------------------------------------------------------------------
# SECTION: LLM - Parser and Chain
# -----------------------------------------------------------------------------
 
class ValidationErrorDetail(BaseModel):
    """
    Pydantic model for detailed error feedback for each agent.
 
    Attributes:
        agent_name (str): The name of the agent with an issue.
        errors (List[str]): List of errors identified in the agent's response.
        suggestions (List[str]): Suggested corrective actions for the errors.
    """
    agent_name: str = Field(description="The name of the agent that generated the output.")
    errors: List[str] = Field(description="List of errors identified in the agent's response.")
    suggestions: List[str] = Field(description="Suggested corrective actions for the errors.")
 

class ObserverValidationResponse(BaseModel):
    """
    Pydantic model for the observer agent response.
 
    Attributes:
        validation_status (bool): Indicates if the overall validation was successful.
        validation_errors (List[ValidationErrorDetail]): Detailed feedback on each agent's errors.
    """
    validation_status: bool = Field(description="Boolean indicating if the overall validation was successful.")
    validation_errors: List[ValidationErrorDetail] = Field(description="Detailed feedback on validation errors.")
 

# Create the output parser
parser = JsonOutputParser(pydantic_object=ObserverValidationResponse)
 
# Define the observer agent chain
observer_agent_chain = observer_agent_prompt | llm_config_loader() | parser
 
# -----------------------------------------------------------------------------
# SECTION: Observer Agent Function
# -----------------------------------------------------------------------------
 
def observer_agent(task_outputs: Dict[str, str], retry_count: int, context: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Validate the outputs of various agents and provide feedback for adjustments.
 
    This function checks the correctness, relevance, and completeness of the outputs from various agents,
    identifies errors, and suggests improvements for further iterations.
 
    Args:
        task_outputs (Dict[str, str]): A dictionary with agent names as keys and their corresponding outputs as values.
        retry_count (int): The current count of retries attempted.
        context (Dict[str, Any]): Additional context or special instructions relevant to the current validation cycle.
 
    Returns:
        Tuple: A tuple containing:
            - bool: A validation status indicating whether the overall output was valid.
            - List[Dict[str, Any]]: Detailed feedback on validation errors and suggestions.
    """
    # Convert task outputs into a format suitable for validation by the observer agent
    validation_input = {
        "task_outputs": task_outputs,
        "retry_count": retry_count,
        "context": context
    }
 
    # Use OpenAI callback to capture token counts
    with get_openai_callback() as cb:
        # Invoke the observer agent chain to validate the outputs
        ai_response = observer_agent_chain.invoke(validation_input)
        input_tokens_count = cb.prompt_tokens
        output_tokens_count = cb.completion_tokens
 
    # Extract the validation status and errors from the response
    validation_status = ai_response.get('validation_status', False)
    validation_errors = ai_response.get('validation_errors', [])
 
    # Return the validation status and detailed error feedback
    return validation_status, validation_errors, input_tokens_count, output_tokens_count
 
# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------