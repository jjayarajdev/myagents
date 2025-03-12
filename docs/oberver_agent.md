# observer_logic_exec

Validates task outputs using an observer agent and manages the retry mechanism for failed validations.

## Overview

The `observer_logic_exec` function manages the quality control process by:

1. **Output Validation:** Using an `observer_agent` to verify the quality and correctness of task outputs.
2. **Retry Management:** Implementing a retry mechanism for when outputs fail validation.
3. **Conversation Tracking:** Updating the conversation history with validated outputs.
4. **Fallback Handling:** Providing a final fallback to a human agent if all retry attempts fail.

## Function Signature

```python
def observer_logic_exec(
    user_input: str,
    task_outputs: List[Dict[str, Any]],
    conversation_history: str,
    user_details: Dict[str, Any],
    total_input_tokens_count: int,
    total_output_tokens_count: int,
    conversation: Dict[str, List[str]],
    retry_context: List
) -> tuple[List[Dict[str, Any]], int, int, Dict[str, List[str]]]
```

## Parameters


| Parameter                   | Type                   | Description                                  |
| ----------------------------- | ------------------------ | ---------------------------------------------- |
| `user_input`                | `str`                  | The user's input string.                     |
| `task_outputs`              | `List[Dict[str, Any]]` | The output from previously executed tasks.   |
| `conversation_history`      | `str`                  | The history of the conversation.             |
| `user_details`              | `Dict[str, Any]`       | A dictionary containing user information.    |
| `total_input_tokens_count`  | `int`                  | The running total of input tokens.           |
| `total_output_tokens_count` | `int`                  | The running total of output tokens.          |
| `conversation`              | `Dict[str, List[str]]` | A dictionary tracking the conversation flow. |
| `retry_context`             | `List`                 | Context from previous failed attempts.       |

## Returns

A tuple containing:

- `task_outputs` (`List[Dict[str, Any]]`): The final (validated) task outputs.
- `total_input_tokens_count` (`int`): Updated total input token count.
- `total_output_tokens_count` (`int`): Updated total output token count.
- `conversation` (`Dict[str, List[str]]`): Updated conversation dictionary.

## Example

```python
# Example usage
final_outputs, input_tokens, output_tokens, updated_conversation = observer_logic_exec(
    user_input="What has been CBRE’s market share in Europe over the past five years?",
    task_outputs=[
        {"function_name": "snowflake_agent", "output": "Error in snowflake Query generation"},
    ],
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
    total_input_tokens_count=1200,
    total_output_tokens_count=800,
    conversation={"conversation_history": [], "present_conversation": [task_outputs=[
        {"function_name": "snowflake_agent", "output": "Error in snowflake Query generation"},
    ]]},
    retry_context=[]
)
```

## Behavior

1. **Retry Loop**:

   - Implements a loop that continues until validation succeeds or maximum retries (`MAX_RETRIES`) are reached
   - Tracks retry count and updates retry context on failures
2. **Task Output Size Check**:

   - Checks if any task output exceeds the maximum token length (`MAXIMUM_AGENT_OUTPUT_TOKEN_LENGTH`)
   - Bypasses validation for oversized outputs to prevent token limit issues
3. **Validation Process**:

   - Uses `observer_agent` to validate task outputs when appropriate
   - Provides conversation history and user details as context for validation
   - Tracks token usage during validation
4. **Successful Validation**:

   - Updates conversation with validated task outputs
   - Formats outputs for usage by downstream agents
5. **Failed Validation**:

   - Logs validation errors
   - Increments retry count
   - Updates retry context with detailed feedback
   - Executes supervisor logic again with updated retry context
6. **Fallback Mechanism**:

   - Falls back to `human_agent` if all retry attempts fail
   - Updates conversation with human agent response
7. **Output Handling**:

   - Returns final task outputs regardless of validation path
   - Returns updated token counts and conversation state
