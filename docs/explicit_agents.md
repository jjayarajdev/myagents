# Explicit Agents Configuration Guide

## Overview

This guide explains how to configure and use explicit agents within the AI agent workflow system. Explicit agents provide a way to extend the functionality of the supervisor agent by allowing you to leverage its outputs and configure additional specialized agents that may not be part of the predefined agent set.

## Table of Contents

- [Understanding Explicit Agents](#understanding-explicit-agents)
- [When to Use Explicit Agents](#when-to-use-explicit-agents)
- [Configuration Process](#configuration-process)
  - [Execution File Structure](#execution-file-structure)
  - [YAML Configuration](#yaml-configuration)
- [Implementation Steps](#implementation-steps)
- [Example: Graph Summary Agent](#example-graph-summary-agent)
- [Enabling and Disabling Agents](#enabling-and-disabling-agents)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Understanding Explicit Agents
s
Explicit agents are specialized agents that can be called directly outside of the supervisor agent's normal workflow. Unlike the agents managed automatically by the supervisor, explicit agents are manually configured and called to perform specific tasks based on the outputs from previous agent interactions.

## When to Use Explicit Agents

Use explicit agents when:

- You need specialized processing capabilities beyond what the standard agent set provides
- You want to extend the system with custom functionality
- You need to process the supervisor agent's outputs in specific ways
- You have a unique workflow that requires custom agent configuration
- You need to chain together multiple specialized agents in a specific sequence

## Configuration Process

### Execution File Structure

The core of explicit agent configuration lies in the `execution.py` file within each agent's folder. This file contains the execution logic for the agent and defines how it processes inputs and generates outputs.

```
project_root/
├── agents_store/
│   ├── graph_summary_agent_prompts/
│   │   ├── execution.py
│   │   ├── system_prompt.yaml
│   │   ├── start_prompt.yaml
│   │   └── example_prompt.yaml
|   |   |__ execution.py

```

### YAML Configuration

Each explicit agent requires its own set of YAML configuration files:

1. `system_prompt.yaml` - Defines the agent's core behavior and capabilities
2. `start_prompt.yaml` - Initializes the agent with appropriate context
3. `example_prompt.yaml` - Provides examples to guide the agent's responses

These files follow the same structure as described in the main AI Agent Configuration Guide.

## Implementation Steps

To configure and use explicit agents:

1. **Identify Required Agents**: Determine which explicit agents you need for your specific use case

2. **Configure Agent YAML Files**: Create or modify the necessary YAML configuration files for each agent

3. **Implement Execution Logic**: Write the execution logic in each agent's `execution.py` file

4. **Register Agents**: Add the agents to the `required_explicit_agents.py` file or call them directly in your code

5. **Test and Refine**: Test the agent workflow and refine the configurations as needed

## Example: Graph Summary Agent

The Graph Summary Agent provides a good example of explicit agent implementation:

```python
def execute(user_input,task_outputs,total_input_tokens_count,total_output_tokens_count,conversation):
    graph_task_outputs = []
    for task in task_outputs:
    
        graph_summary_input = {
            "user_input" : user_input,
            "other_agents_response": task["output"]
        }

        task_output,input_tokens_count,output_tokens_count = generic_agent("graph_summary_agent",graph_summary_input)
        total_input_tokens_count += input_tokens_count
        total_output_tokens_count += output_tokens_count
        graph_task_outputs.append({
            "output": task_output
        })

        conversation["present_conversation"].append({"graph_summary_agent": task_output})

        return graph_task_outputs,total_input_tokens_count,total_output_tokens_count,conversation
```

This example shows how the Graph Summary Agent iterates through task outputs from the supervisor agent and passes them as inputs to the generic agent, configured specifically for graph summarization.

## Enabling and Disabling Agents

To enable or disable explicit agents:

1. Open the `required_explicit_agents.py` file
2. Add or uncomment the import and function call for the agents you want to enable
3. Comment out or remove the function calls for agents you want to disable

Example:

```python
# required_explicit_agents.py
from agents_store.graph_summary_agent.execution import execute as graph_summary_execute

def explicit_agents(
    user_input,
    task_outputs,
    total_input_tokens_count,
    total_output_tokens_count,
    conversation
):

    graph_summary_task_outputs,total_input_tokens_count,total_output_tokens_count,conversation = graph_summary_execute(
        user_input,
        task_outputs,
        total_input_tokens_count,
        total_output_tokens_count,
        conversation
    )
    return total_input_tokens_count,total_output_tokens_count,conversation

```

If your code is already calling the required agents directly, there's no need to add additional code in `required_explicit_agents.py`.


## Troubleshooting

If you encounter issues with explicit agents:

1. **Check YAML Configuration**: Ensure all required YAML files are correctly formatted
2. **Verify Function Calls**: Check that the correct execution functions are being called
3. **Inspect Input Data**: Verify that the correct input data is being passed to the agents
4. **Check for Errors**: Look for error messages in the execution logs
5. **Test Individually**: Test each agent individually to isolate issues
6. **Review Documentation**: Consult the agent documentation for specific requirements