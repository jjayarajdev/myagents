from agents_store.graph_summary_agent.execution import execute as graph_summary_execute
from agents_store.summary_agent.execution import execute as summary_execute

def explicit_agents(
    user_input,
    task_outputs,
    total_input_tokens_count,
    total_output_tokens_count,
    conversation,user
):

    # graph_summary_task_outputs,total_input_tokens_count,total_output_tokens_count,conversation = graph_summary_execute(
    #     user_input,
    #     task_outputs,
    #     total_input_tokens_count,
    #     total_output_tokens_count,
    #     conversation,user
    # )
    summary_task_outputs,total_input_tokens_count,total_output_tokens_count,conversation = summary_execute(
        user_input,
        task_outputs,
        total_input_tokens_count,
        total_output_tokens_count,
        conversation,user
    )


    return total_input_tokens_count,total_output_tokens_count,conversation
