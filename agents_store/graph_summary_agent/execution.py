# from agents_store.graph_summary_agent.generic_agent import generic_agent
from agents import generic_agent

#----------------------------------------------------------------------------
# This function executes the explicit agent logic and calls the generic agent
#----------------------------------------------------------------------------
def execute(user_input,task_outputs,total_input_tokens_count,total_output_tokens_count,conversation,user):
    """
    Processes task outputs through a graph summary agent and updates the conversation history.
    
    This function takes the outputs from previously executed tasks and processes each one
    through a graph summary agent, which creates visual data points or structured summaries of agent
    responses. The function tracks token usage and updates the conversation context with
    the summary outputs.
    
    Args:
        user_input (str): The original user query or input text.
        task_outputs (list): A list of dictionaries containing the outputs from previous tasks,
                            where each dictionary has at least an "output" key.
        total_input_tokens_count (int): Running count of input tokens used in the workflow.
        total_output_tokens_count (int): Running count of output tokens used in the workflow.
        conversation (dict): Dictionary containing conversation history, with a 
                            "present_conversation" key that holds a list of message exchanges.
    
    Returns:
        tuple: A tuple containing:
            - graph_task_outputs (list): List of dictionaries with summarized outputs.
            - total_input_tokens_count (int): Updated input token count.
            - total_output_tokens_count (int): Updated output token count.
            - conversation (dict): Updated conversation history with summary responses.
    """

    #---------------------------------------------------------------------------------------------------------
    # Execute the business logic by preparing the required input parameters and invoking the appropriate agent
    #---------------------------------------------------------------------------------------------------------
    graph_task_outputs = []
    for task in task_outputs:
    
        graph_summary_input = {
            "user_input" : user_input,
            "other_agents_response": task["output"]
        }

        task_output,input_tokens_count,output_tokens_count = generic_agent("graph_summary_agent",graph_summary_input,user)
        total_input_tokens_count += input_tokens_count
        total_output_tokens_count += output_tokens_count
        graph_task_outputs.append({
            "output": task_output
        })

        conversation["present_conversation"].append({"summary_agent": task_output})

        return graph_task_outputs,total_input_tokens_count,total_output_tokens_count,conversation

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------