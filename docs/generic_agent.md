# generic_agent

Creates and executes a generic AI agent pipeline based on specified function configuration.

## Overview

The `generic_agent` function sets up a configurable AI agent that:

1. Loads necessary prompts from a directory structure
2. Creates a pipeline with system, schema, example, and start prompts
3. Generates appropriate output models based on parameter specifications
4. Executes the pipeline and optionally processes results through database query execution based on the

## Function Signature

```python
def generic_agent(
    function_name: str,
    func_params: dict
) -> tuple[Any, int, int]
```

## Parameters


|    Parameter    | Type   | Description                                                                                                      |
| :---------------: | :------- | ------------------------------------------------------------------------------------------------------------------ |
| `function_name` | `str`  | Name of the function configuration to use. This determines which prompt directory and utility functions to load. |
|  `func_params`  | `dict` | Parameters to pass to the prompt templates and agent pipeline.                                                   |

## Returns

A tuple containing:

- `ai_response`: The processed response from the AI model
- `input_tokens_count` (`int`): Number of tokens in the input prompt
- `output_tokens_count` (`int`): Number of tokens in the model's response

## Example

```python
# Example usage
response, input_tokens, output_tokens = generic_agent(
    function_name="db_agent",
    func_params={
        "user_input": "What has been CBRE’s market share in Europe over the past five years?"
    }
)
```

## Behavior

1. **Directory Structure**:

   - Looks for a directory named `{function_name}_prompts`
   - Expects to find system, schema, example, and start prompts in YAML format
2. **Prompt Processing**:

   - Loads prompts from YAML files
   - Creates chat prompt templates
   - Combines them into a pipeline prompt template
3. **Output Model Generation**:

   - Dynamically creates Pydantic models based on output parameter specifications
   - Supports nested models for complex output structures
4. **Database Operations** (conditional):

   - If a database operation configuration is found, uses specialized prompt loading and execution
   - Can execute database queries based on the generated AI response
5. **Response Processing**:

   - Parses JSON responses into appropriate structures
   - Tracks token usage for input and output
