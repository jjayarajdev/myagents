# supervisor_logic_exec

Based on the user's input supervisor agent will break it down into list of tasks. These tasks are executed in a sequence in supervisor logic

## Overview

The `supervisor_logic_exec` function orchestrates the process of:

1. **Task Generation:** Uses a `supervisor_agent` to create a list of tasks based on user input, conversation history, user details, and previous retry attempts. The supervisor agent handles task decomposition.
2. **Task Execution:** Executes the generated tasks using the `execute_tasks` function.
3. **Token Counting:** Tracks the total input and output tokens consumed during both task generation and execution.

## Function Signature

```python
def supervisor_logic_exec(
    user_input: str,
    conversation_history: str,
    user_details: Dict[str, Any],
    total_input_tokens_count: int,
    total_output_tokens_count: int,
    retry_context: List
) -> tuple[list[Any], int, int, list[str]]
```

## Parameters


| Parameter                   | Type             | Description                                                     |
| ----------------------------- | ------------------ | ----------------------------------------------------------------- |
| `user_input`                | `str`            | The user's input string.                                        |
| `conversation_history`      | `str`            | The history of the conversation.                                |
| `user_details`              | `Dict[str, Any]` | A dictionary containing user information (e.g., name, country). |
| `total_input_tokens_count`  | `int`            | The running total of input tokens.                              |
| `total_output_tokens_count` | `int`            | The running total of output tokens.                             |
| `retry_context`             | `List`           | Context from previous failed attempts.                          |

## Returns

A tuple containing:

- `task_outputs` (`List[Any]`): The results of executing the tasks.
- `input_tokens_count` (`int`): Updated total input token count.
- `output_tokens_count` (`int`): Updated total output token count.

## Example

```python
# Example usage
task_results, input_tokens, output_tokens = supervisor_logic_exec(
    user_input="What has been CBRE’s market share in Europe over the past five years?",
    conversation_history="Previous conversation...",
    user_details={
        "country": "India",
        "country_code": "IN",
        "market": "None",
        "sector": "ALL",
        "user_id": "1",
        "user_mail": "example@cbre.com",
        "user_name": "example"
    },
    total_input_tokens_count=0,
    total_output_tokens_count=0,
    retry_context=[]
)
```

## Behavior

1. **Task Generation**:

   - Calls `supervisor_agent` with user details, input, conversation history, and retry context
   - The supervisor agent analyzes the request and decomposes it into specific tasks
2. **Token Tracking**:

   - Accumulates input and output token counts from the supervisor agent
3. **Task Execution**:

   - Passes the generated task list to the `execute_tasks` function
   - Collects the results of each executed task
4. **Logging**:

   - Logs the supervisor agent's output for debugging and monitoring purposes
5. **Return Values**:

   - Returns task execution outputs, updated token counts, and potentially a list of result logs
