# AI Agent Configuration Guide

This comprehensive guide provides detailed instructions for configuring and effectively utilizing generative AI agents in your workflow.

## Table of Contents

- [Installation](#installation)
- [Agent Configuration Process](#agent-configuration-process)
- [Configuration Files](#configuration-files)
  - [agent_required.yaml](#agent_requiredyaml)
  - [System Prompt](#system-prompt)
  - [Start Prompt](#start-prompt)
  - [Example Prompt](#example-prompt)
  - [Schema Prompt](#schema-prompt)
- [Usage Patterns](#usage-patterns)
  - [Workflow Graph](#workflow-graph)
  - [Supervisor Logic](#supervisor-logic)
  - [Observer Logic](#observer-logic)
- [Sample Agent YAML Files](#sample-agent-yaml-files)
- [Explicit Agents](#agent-configuration-process)

## Installation

TBD

## Agent Configuration Process

The agent configuration process involves several key steps:

1. Configure `agent_required.yaml` as the main configuration file that defines which agents will be utilized in your workflow.
2. Create specific prompt files based on the agent type:

   - `system_prompt.yaml` - Defines core agent behavior and capabilities
   - `start_prompt.yaml` - Initializes the conversation flow
   - `example_prompt.yaml` - Provides sample interactions for agent guidance
   - `schema_prompt.yaml` - Required specifically for database agents
3. Package all configuration files into a ZIP archive for deployment and distribution

### agent_required.yaml

In this file, you configure the specific agents that you want to make available to the supervisor agent. The supervisor will select appropriate agents based on task requirements and context.

Sample file:

```yaml
agents_required:
  - generic_conversation_agent
  - db_agent
  - human_agent
```

### System Prompt

The system prompt provides fundamental instructions that shape the agent's behavior and capabilities. It establishes the core identity and skills of the agent, setting boundaries for how it will respond to various inputs. This is defined in `system_prompt.yaml`:

Sample File:

```yaml
system_prompt: |
  **System:**  
  You are Ellis, an AI assistant capable of performing various tasks based on user input.

Tasks:
  - Task-1: |
      **Your Tasks:**  
      1. **Evaluate Input Coherence Before Splitting:**
            - Split: Break down the input into multiple tasks if it contains distinct, related factors or aspects that can be checked separately. For example, if the input asks for different types of analyses or metrics (like revenue and number of transactions), these should be treated as separate tasks.  
            - Avoid Duplication: Check for overlap among tasks. Do not create multiple tasks for the same input or context.

            Examples:  
            - Input: "What factors contributed to the decline in market share for CBRE in France, such as the number of transactions and revenue?"
            - Correct Behavior: Create two tasks, one focusing on the number of transactions and the other on revenue.  
            - Input: "What are the trends in market share for CBRE in France?"
            - Correct Behavior: Handle as a single task, unless distinct sub-questions are specified.

      **Instructions for Input Coherence evaluation Before Splitting**
              -Identify the Main Components: Analyze the complex question to identify its main components or subtopics. Break down the question into smaller, more specific questions that address each component.
              -Generate Detailed Responses: For each smaller question, generate a detailed response that thoroughly addresses the specific aspect of the main question.
              -Combine Responses: After generating responses for all smaller questions, combine these responses into a cohesive and comprehensive final answer. Ensure that the final answer logically integrates all the information and provides a clear and complete response to the original complex question.
              -Maintain Clarity and Coherence: Ensure that the final combined answer is clear, coherent, and easy to understand. Use appropriate transitions and connections between different parts of the answer to maintain a smooth flow of information.
      - Avoid Duplication: Check for overlap among tasks. Do not create multiple tasks for the same input or context.

Instructions:
  - Instruction-1: |
      **Prioritize Clarity and Simplicity:**  
      - Avoid redundant or repetitive phrasing in tasks.  
      - Include all relevant sub-contexts (e.g., "Industrial/Retail/Office") in the same task rather than splitting them.  

Notes:
  - Note-1: |
      **Note**:
      **User Input Interpretation Guidelines**
              -If the user input includes "we," please interpret the question as referring to CBRE.
      ---
```

### Start Prompt

The start prompt initializes the conversation and sets expectations for the user. It establishes the context for the interaction and defines key parameters that will be used throughout the conversation. This template contains placeholders that will be dynamically populated during execution. This is defined in `start_prompt.yaml`:

```yaml
start_prompt: |
  **Input:**
  from-user-name: {user_name}
  user-input: {user_input}
  user-country: {user_country}
  full-user-details: {full_user_details}
  conversation-history: {conversation_history}
  retry_context: {retry_context}
```

### Example Prompt

The example prompt provides sample interactions to guide the agent's behavior by showing concrete examples of expected inputs and appropriate responses. These examples serve as training material for the agent to learn proper response patterns and decision-making processes. It's defined in `example_prompt.yaml`:

```yaml
Examples:
  - Example-1:
      Input: |
        Input: Factors contributed to the decline in market share for CBRE

      Reasoning: |

      Correct_Behaviour: |
        **Correct Behavior:** Create **multiple tasks**, as the question is to identify the factors.  
        Task-1: Calculating number of Transactions: Evaluate the total number of transactions processed over a specific period. This metric helps in understanding the volume of business activity and customer engagement.
        Task-2: Calculating the Transaction Value: Assess the total value of transactions processed. This metric provides insight into the revenue generated and the average transaction size.

      Incorrect_Behaviour: |
        **Incorrect Behavior:** Combine into a single task or create multiple overlapping tasks.
```

### Schema Prompt

The schema prompt is required specifically for database agents to define the database structure and fields. It provides the agent with detailed information about available data sources, their properties, and appropriate usage contexts. This enables the agent to properly query and interpret database information. It's defined in `schema_prompt.yaml`:

```yaml
schema:
  Table_Schema: Schema
    NOTE: "THIS IS SOLELY FOR INTERNAL COMPANY RESEARCH AND EXPERIMENTATION PURPOSE ONLY."
    Columns:
      - Column1: |
            Name:PROPERTY_ID
            Description: This column is a unique ID for the land parcel/building - a building can be sold many times, so this may be repeated. Use the distinct PROPERTY_ID column to calculate the number of transactions."
            Data_Type: VARCHAR(16777216)
      - Column2: |
            Name:BROKERAGEFIRM
            Description:The name of the real estate brokerage firm representing the buyer or seller in transactions. This identifies the entity that facilitates the buying or selling process.
                        - Also referred to as "Broker Company", "Representative", "Broker".
            Data_Type: VARCHAR(16777216)
      - Column3: |
            Name:BUYERMARKETSHARE
            Description: "The total monetary value of real estate transactions where buyers were represented by a specific brokerage firm. Do consider this column when the question is about buyer broker Sales Volume (AKA Transaction volume, deal volume, total consideration)."
            Data_Type: FLOAT
      - Column4: |
          Name:SELLERMARKETSHARE
          Description: "The total monetary value of real estate transactions where sellers were represented by a specific brokerage firm. This figure reflects the aggregate amount of transactions completed by that firm on behalf of sellers in the market during a specific time period. Do consider this column when the question is about seller broker Sales Volume (AKA Transaction volume, deal volume, total consideration, Seller Wallet Share, Listing Market Share)."
          Data_Type: FLOAT
```

## Usage Patterns

After configuration, there are several key patterns for utilizing AI agents effectively within your workflow. Understanding these patterns is essential for creating robust and flexible agent-based systems.

### Workflow Graph

The workflow graph serves as the orchestration layer for agent execution. It functions as the central control mechanism through which all other agents are spawned and managed. The workflow graph can be configured by passing the following essential parameters:

* `user_input` - The query or instruction from the end user
* `conversation_history` - Previous interactions for maintaining context
* `user_details` - Relevant information about the user for personalization

Below is the code to call the workflow graph:

```python
response = ask_ellis_workflow_graph(user_input, conversation_history, user_details)
```

This initiates the entire agent workflow process, starting with the supervisor logic.

### Supervisor Logic

From the workflow graph, the supervisor_logic is called and handles task division and execution of the tasks. In supervisor_logic, a dedicated supervisor agent is called which analyzes the user question and divides it into appropriate subtasks.

Within these tasks, the supervisor agent specifies which specialized agents should be called based on the nature of the questions and required expertise. These tasks will execute in sequence by calling the `generic_agent()` function. The generic agent processes the inputs and returns the appropriate response.

The supervisor logic ensures that complex queries are broken down appropriately and routed to the most suitable specialized agents, then aggregates their responses into a coherent whole.

### Observer Logic

After getting the outputs from the supervisor_logic, observer_logic is called and executes the observer_agent. This agent acts as a quality control mechanism that verifies if there are any errors that have occurred at the supervisor_logic level.

If the observer_agent detects an error or inconsistency, it will call the supervisor_logic again with a fresh perspective to re-execute the user query. It provides feedback about what errors the supervisor agent made in the previous attempt, allowing for a self-correcting system that improves response quality through multiple passes when necessary.

This multi-layered approach ensures higher accuracy and reliability in complex workflows.

## Calling Agents Explicitly out of the supervisor agent

Calling agents explicitly is particularly useful when you want to leverage the supervisor agent's outputs and configure new agents that aren't part of the supervisor agent's predefined set. This provides greater flexibility in extending the system's capabilities for specialized tasks or unique workflows.

#### Configuration of the Explicit agents

For configuring explicit agents, the execution logic should be written in the `execution.py` file. You can modify various parameters and utilize task outputs based on your specific use case requirements.

For example, in the `graph_summary_agent.py`, the logic is designed to iterate through all tasks from previous agent outputs and pass those outputs as inputs to the generic agents. This is done by configuring the YAML files
