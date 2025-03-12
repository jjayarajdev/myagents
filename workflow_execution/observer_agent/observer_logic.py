
# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------
import logging
import os
from typing import Any, Dict, List

from workflow_execution.observer_agent.observer_agent import observer_agent
from agents.core_engine_agents.human_agent import human_agent
from workflow_execution.supervisor_agent.supervisor_logic import supervisor_logic_exec
from utils.helper_functions import compute_total_length

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

MAX_RETRIES = int(os.getenv("ERROR_TOLERANCE_COUNT"))
MAXIMUM_AGENT_OUTPUT_TOKEN_LENGTH = int(os.getenv("MAXIMUM_AGENT_OUTPUT_TOKEN_LENGTH"))

#--------------------------------------------
# SECTION : Observer agent logic execution
#--------------------------------------------
def observer_logic_exec(
    user_input: str,
    task_outputs: List[Dict[str, Any]],
    conversation_history: str, 
    user_details: Dict[str, Any],
    total_input_tokens_count: int,
    total_output_tokens_count: int,
    conversation: Dict[str, List[str]],
    retry_context: List,
    user: str
)->tuple[List[Dict[str, Any]], int, int, Dict[str, List[str]]]:
    
    #initialize the retry count
    retry_count = 0
    while retry_count <= MAX_RETRIES:

        if retry_count > 0:

            task_outputs,total_input_tokens_count,total_output_tokens_count = supervisor_logic_exec(
                user_input,
                conversation_history,
                user_details,
                total_input_tokens_count,
                total_output_tokens_count,
                retry_context,user
            )

        print('*' * 50)
        print("Retry Count = ", retry_count)
        print('*' * 50)

        
        # Bypass the observer agent if length of the task outputs exceeds a certain threshold
        if all(compute_total_length(task["output"]) < MAXIMUM_AGENT_OUTPUT_TOKEN_LENGTH for task in task_outputs):

            # Step 3: Validate all agent responses using observer agent
            # Pass the task outputs, retry count, and additional context to the observer agent
            is_valid, validation_errors, input_tokens_count, output_tokens_count = observer_agent(
                task_outputs=task_outputs,
                retry_count=retry_count,
                context={"conversation_history": conversation_history, "user_details": user_details}
            )
            total_input_tokens_count += input_tokens_count
            total_output_tokens_count += output_tokens_count

            if is_valid:
                # Append task outputs to the present conversation
                conversation["present_conversation"].extend(
                    [{task["function_name"]: task["output"]} for task in task_outputs]
                )

                # Generate the agents' response summary for the final Q&A agent
                agents_response = "\n".join(
                    f"{task['function_name']}: {task['output']}"
                    for task in task_outputs
                )

                break  # Exit the retry loop if successful

            else:
                # Log validation errors and retry, update retry context with feedback
                logger.error("Validation failed with errors: %s", validation_errors)
                retry_count += 1
                retry_context.append({
                    "attempt": retry_count,
                    "errors": validation_errors,
                    "task_outputs": task_outputs,
                    "suggested_corrections": "Consider adjusting agent selection or parameters based on errors."
                })

                if retry_count > MAX_RETRIES:
                    # Final fallback to human agent if retries are exhausted
                    conversation["present_conversation"].append(
                        {
                            "human_agent": human_agent({
                                'input_text': user_input,
                                'conversation_history': conversation_history,
                                'user_details': user_details
                            })
                        }
                    )
                    break
        else:
            # Bypass the observer agent and append task outputs to the present conversation
            conversation["present_conversation"].extend(
                [{task["function_name"]: task["output"]} for task in task_outputs]
            )
            break

    return task_outputs,total_input_tokens_count,total_output_tokens_count,conversation

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------