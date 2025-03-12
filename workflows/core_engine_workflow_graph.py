"""
Module Name: core_engine_workflow_graph.py

Description:
This module implements a custom workflow graph for the Ask Ellis system, integrating
various agents and maintaining conversation history. The graph coordinates task execution
among agents, resolves dependencies, and tracks token usage during the conversation.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
from typing import Any, Dict, List
import logging
import os
import traceback

# Local application imports
from agents.core_engine_agents.dependency_resolver_agent import dependency_resolver
from agents.core_engine_agents.conversation_summary_agent import conversation_summary_agent
from agents.generic_conversation_agent import generic_conversation_agent
from agents.generic_agent import generic_agent
from agents_store.db_agent.utils.query_repository import Queries
from required_explicit_agents import explicit_agents
from workflow_execution.observer_agent.observer_logic import observer_logic_exec
from workflow_execution.supervisor_agent.supervisor_logic import supervisor_logic_exec
from workflow_execution.explicit_agent.explicit_agent_logic import explicit_logic_exec

# Third-party imports
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# SECTION: Logger Setup
# -----------------------------------------------------------------------------

# Get a logger instance for this module
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# SECTION: Environment Setup
# -----------------------------------------------------------------------------

# Load environment variables from .env file
load_dotenv()

# Maximum length of conversation history after which it will be summarized

MAXIMUM_CONVERSATION_HISTORY_LENGTH = int(os.getenv("MAXIMUM_CONVERSATION_HISTORY_LENGTH"))
logger.info(f"Maximum conversation history length set to: {MAXIMUM_CONVERSATION_HISTORY_LENGTH}")

# -----------------------------------------------------------------------------
# SECTION: Workflow Graph Implementation
# -----------------------------------------------------------------------------
 
def ask_ellis_workflow_graph(user_input: str, conversation_history: str, user_details: Dict[str, Any],user) -> Dict[str, Any]:
    """
    Main workflow function that coordinates the execution of various agents in the Ask Ellis system.
    
    Args:
        user_input (str): The current input from the user
        conversation_history (str): Previous conversation history
        user_details (Dict[str, Any]): User information and context
        
    Returns:
        Dict[str, Any]: Final conversation details, generated query, and token counts
    """
    logger.info("Starting ask_ellis_workflow_graph execution")
    logger.info(f"Processing user input: {user_input[:50]}..." if len(user_input) > 50 else f"Processing user input: {user_input}")

    # Initialize token counts and retry counters
    total_input_tokens_count = 0
    total_output_tokens_count = 0
    retry_context = []  # To store information about previous attempts and failures

    # Initialize conversation and task outputs
    conversation = {
        "conversation_history": conversation_history,
        "present_conversation": []
    }
    conversation["present_conversation"].append({"user_input": user_input})
    logger.info("Initialized conversation structure")

    try:
        # Calls supervisor agent logic and returns the output of the supervisor agent
        logger.info("Executing supervisor agent logic")
        task_outputs, total_input_tokens_count, total_output_tokens_count = supervisor_logic_exec(
                user_input,
                conversation_history,
                user_details,
                total_input_tokens_count,
                total_output_tokens_count,
                retry_context=retry_context,
                user=user
            )
        logger.info(f"Supervisor agent execution complete. Input tokens: {total_input_tokens_count}, Output tokens: {total_output_tokens_count}")
    except Exception as e:
        logger.error(f"Error in supervisor agent execution: {str(e)}")
        logger.debug(traceback.format_exc())
        # Initialize with empty task outputs if supervisor fails
        task_outputs = {}

    try:
        # Calls the observer agent logic
        logger.info("Executing observer agent logic")
        task_outputs, total_input_tokens_count, total_output_tokens_count, conversation = observer_logic_exec(
            user_input,
            task_outputs,
            conversation_history,
            user_details,
            total_input_tokens_count,
            total_output_tokens_count,
            conversation,
            retry_context,user
        )
        logger.info(f"Observer agent execution complete. Input tokens: {total_input_tokens_count}, Output tokens: {total_output_tokens_count}")
    except Exception as e:
        logger.error(f"Error in observer agent execution: {str(e)}")
        logger.debug(traceback.format_exc())
        # Prevent complete workflow failure if observer fails

    print('\n')
    print('*' * 50)
    print("Invoking Explicit Agents")
    print('*' * 50)
    print('\n')

    logger.info("Invoking explicit agents")
    
  
    #---------------------------------------------------------------------------------------------
    # SECTION: Calling Summary Agent by writing the code. 
    # The code can be written in case of input of one agent depends on the explicit agent outputs
    #---------------------------------------------------------------------------------------------
    logger.info("Executing additional explicit agents")
    
    try:
        total_input_tokens_count, total_output_tokens_count, conversation = explicit_agents(
            user_input,
            task_outputs,
            total_input_tokens_count,
            total_output_tokens_count,
            conversation,user
        )
        logger.info(f"Additional explicit agents execution complete. Input tokens: {total_input_tokens_count}, Output tokens: {total_output_tokens_count}")
    except Exception as e:
        logger.error(f"Error in additional explicit agents execution: {str(e)}")
        logger.debug(traceback.format_exc())

    
    query = getattr(Queries, "query", "No query generated")
    logger.info(f"Final query generated: {query[:100]}..." if len(str(query)) > 100 else f"Final query generated: {query}")
    print(query)
    
    # Return final conversation details and token counts
    logger.info(f"Workflow complete. Total input tokens: {total_input_tokens_count}, Total output tokens: {total_output_tokens_count}")
    return {
        "conversation": conversation,
        "generated_snowflake_query": query,
        "input_tokens_count": total_input_tokens_count,
        "output_tokens_count": total_output_tokens_count
    }
 
# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------