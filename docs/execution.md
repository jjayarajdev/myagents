# Agent Execution Documentation

## Module Overview

The `execute` function is a core component of an agent system that processes task outputs to generate structured summaries or visual representations. It works by taking outputs from previous task executions and processing them through a generic agent framework.

## Function: `execute`

```python
def execute(user_input, task_outputs, total_input_tokens_count, total_output_tokens_count, conversation):
```

### Purpose

This function processes previous task outputs through a specialized agent, which creates structured summaries or visual representations of agent responses. It tracks token usage and updates the conversation context.

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `user_input` | `str` | The original user query or input text |
| `task_outputs` | `list` | List of dictionaries containing outputs from previous tasks (each with at least an "output" key) |
| `total_input_tokens_count` | `int` | Running count of input tokens used in the workflow |
| `total_output_tokens_count` | `int` | Running count of output tokens used in the workflow |
| `conversation` | `dict` | Dictionary containing conversation history with a "present_conversation" key holding message exchanges |

### Returns

A tuple containing:
- `agent_task_outputs` (`list`): List of dictionaries with processed outputs
- `total_input_tokens_count` (`int`): Updated input token count
- `total_output_tokens_count` (`int`): Updated output token count
- `conversation` (`dict`): Updated conversation history with agent responses

### Process Flow

1. Initializes an empty list to store agent task outputs
2. Iterates through each task in the provided task outputs
3. For each task:
   - Prepares input for the specialized agent
   - Calls the generic agent with the appropriate agent configuration
   - Updates token counts
   - Appends the result to agent task outputs
   - Updates the conversation history
4. Returns the results as a tuple

### Dependencies

- Relies on the `generic_agent` function from an agent store module
- Requires properly formatted task outputs and conversation structure

## Usage Example

```python
# Example usage
user_query = "Analyze the sales trends for Q3"
previous_results = [{"output": "Sales increased by 15% in North America..."}, 
                   {"output": "European market showed 7% decline in electronics..."}]
input_tokens = 450
output_tokens = 680
conv_history = {"present_conversation": [{"user": user_query}]}

processed_outputs, updated_in_tokens, updated_out_tokens, updated_conv = execute(
    user_query, 
    previous_results, 
    input_tokens, 
    output_tokens, 
    conv_history
)
```

## Notes

- The function maintains a cumulative count of tokens used throughout the workflow
- Each processed output is appended to the conversation history under an agent-specific key
- The generic agent is expected to handle the actual processing logic based on the agent type