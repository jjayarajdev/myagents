# from agents_store.graph_summary_agent.generic_agent import generic_agent
from agents.generic_agent import generic_agent
#----------------------------------------------------------------------------
# This function executes the explicit agent logic and calls the generic agent
#----------------------------------------------------------------------------
def execute(user_input,task_outputs,total_input_tokens_count,total_output_tokens_count,conversation,user):
    """
    Aggregates summaries from task outputs and generates a consolidated summary through a summary agent.
    
    This function extracts individual summaries from previously executed tasks, combines them,
    and processes them through a summary agent to create a unified response. The function tracks
    token usage, updates the conversation context with the final summary, and returns the
    consolidated summary along with updated token counts.
    
    Args:
        user_input (str): The original user query or input text.
        task_outputs (list): A list of dictionaries containing the outputs from previous tasks,
                            where each dictionary has an "output" key with a nested "summary" key.
        total_input_tokens_count (int): Running count of input tokens used in the workflow.
        total_output_tokens_count (int): Running count of output tokens used in the workflow.
        conversation (dict): Dictionary containing conversation history, with a 
                            "present_conversation" key that holds a list of message exchanges.
    
    Returns:
        tuple: A tuple containing:
            - task_output (dict): The output from the summary agent, containing a consolidated summary.
            - total_input_tokens_count (int): Updated input token count.
            - total_output_tokens_count (int): Updated output token count.
            - conversation (dict): Updated conversation history with the consolidated summary.
    """
    #---------------------------------------------------------------------------------------------------------
    # Execute the business logic by preparing the required input parameters and invoking the appropriate agent
    #---------------------------------------------------------------------------------------------------------
    try:
        summaries = []
        for task in task_outputs:
            summaries.append(task['output'])
        summary_input = {
                    "user_input": user_input,
                    "other_agents_response": summaries
                }
        
        task_output,input_tokens_count,output_tokens_count = generic_agent("summary_agent",summary_input,user)
        conversation["present_conversation"].append({"summary_agent": task_output['summary']}) 
        total_input_tokens_count += input_tokens_count
        total_output_tokens_count += output_tokens_count

        return task_output,total_input_tokens_count,total_output_tokens_count,conversation
    except Exception as e:
        print(f"Error in executing the summary agent: {str(e)}")
        return {},total_input_tokens_count,total_output_tokens_count,conversation

