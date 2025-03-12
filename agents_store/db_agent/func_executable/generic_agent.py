"""

Module Name: generic_agent.py

This module provides a flexible and configurable framework for creating AI agents with dynamic
functionality. It enables the creation of generic AI agents that can be customized through
prompt-based configuration and dynamic model generation.
"""

# -----------------------------------------------------------------------------
# SECTION: Generic Agent Function with Dynamic Imports
# -----------------------------------------------------------------------------

from typing import List, Optional, Any, Dict, Tuple
import json
import logging
from pathlib import Path

# Third-party imports that are required
from langchain_community.callbacks import get_openai_callback
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.prompts.pipeline import PipelinePromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, create_model

# Local application imports that are required
from utils.helper_functions import load_prompt, load_prompt_yaml, find_directory, get_output_params
from models.openai.azure_openai_model import llm_config_loader

# Import the dynamic import utilities
from utils.dynamic_imports import (
    lazy_import_db_dependencies,
    get_dboconfig_safe,
    load_db_prompts,
    execute_db_query,
    add_query_to_repository
)

logger = logging.getLogger(__name__)

def create_generic_output_model(model_name, params, data_types) -> BaseModel:
    """
    Creates a dynamic Pydantic model with specified fields and data types.
    
    This function generates a new Pydantic model class at runtime based on the provided
    parameter names and their corresponding data types. Each field in the resulting model
    is created with a generic description.
    
    Args:
        model_name (str): The name to be given to the generated Pydantic model class.
            This name should be unique to avoid conflicts with existing models.
        
        params (List[str]): A list of parameter names that will become field names
            in the generated model. Each name should be a valid Python identifier.
            Example: ["name", "age", "email"]
        
        data_types (List[Type]): A list of Python/Pydantic types corresponding to each
            parameter. The types can be basic Python types (str, int, float, etc.) or
            complex Pydantic models.
            Example: [str, int, EmailStr]
            
    Returns:
        Type[BaseModel]: A new Pydantic model class with the specified fields
            and data types.
    """
    try:
        logger.info(f"Creating dynamic Pydantic model: {model_name} with {len(params)} fields")
        field_definitions = {}
        for idx in range(len(params)):
            field_definitions[params[idx]] = (
                data_types[idx], 
                Field(description="This is generic Pydantic class")
            )
        
        GenericOutput = create_model(model_name, **field_definitions)
        logger.info(f"Successfully created dynamic model: {model_name}")
        return GenericOutput
    except Exception as e:
        logger.error(f"Error creating dynamic Pydantic model {model_name}: {str(e)}")
        raise

def get_subparams(sub_params):
    """
    Extracts values and data types from sub-parameters.
    
    Args:
        sub_params: List of sub-parameter dictionaries
        
    Returns:
        Tuple of sub-parameter values and data types
    """
    try:
        logger.info(f"Extracting sub-parameters from {len(sub_params)} parameter groups")
        sub_params_values = []
        sub_params_datatypes = []

        for params in sub_params:
            for key in params.keys():
                sub_params_values.append(params[key]['value'])
                sub_params_datatypes.append(params[key]['data_type'])
        
        return sub_params_values, sub_params_datatypes
    except KeyError as e:
        logger.error(f"Missing key in sub_params structure: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting sub-parameters: {str(e)}")
        raise

def generic_agent(
    function_name: str,
    func_params: dict
) -> tuple[Any, int, int]:
    """
    Creates and executes a generic AI agent pipeline based on specified function configuration.
    
    This function sets up a configurable AI agent that:
    1. Loads necessary prompts from a directory structure
    2. Creates a pipeline with system, schema, example, and start prompts
    3. Generates appropriate output models based on parameter specifications
    4. Executes the pipeline and optionally processes results through utility functions
    
    Args:
        function_name (str): Name of the function configuration to use. This determines
            which prompt directory and utility functions to load.
        func_params (dict): Parameters to pass to the prompt templates and agent pipeline.
    
    Returns:
        tuple: A tuple containing:
            - ai_response: The processed response from the AI model
            - input_tokens_count (int): Number of tokens in the input prompt
            - output_tokens_count (int): Number of tokens in the model's response
    """
    logger.info(f"Starting generic agent execution for function: {function_name}")
    
    # Variable Initialisation
    param_names = []
    data_types = []
    subparams_values = None
    subparams_datatypes = None
    # Combined Token Counts of table pruning agent and generic agent
    combined_input_tokens_count = 0
    combined_output_tokens_count = 0

    try:
        directory_name = function_name + "_prompts"
        output_params = get_output_params(function_name)
        logger.info(f"Retrieved {len(output_params)} output parameters for {function_name}")
        
        directory = find_directory(Path.cwd(), directory_name)
        directory = r"{}".format(directory)
        logger.info(f"Found prompt directory at: {directory}")
        
        start_text = load_prompt_yaml(directory + r"\start_prompt.yaml")
        logger.info("Successfully loaded start prompt")

        # -----------------------------------------------------------------------------
        # SECTION: Dynamic DB Configuration Check
        # -----------------------------------------------------------------------------
        # Try to get DB config safely (returns None if not available)
        dboconfig = get_dboconfig_safe(function_name)
        logger.info(f"DB configuration for {function_name}: {dboconfig if dboconfig else 'None'}")
        
        # If we have a DB config, try to load DB-specific prompts
        if dboconfig is not None:
            # Get all DB dependencies
            logger.info("Loading database dependencies")
            db_deps = lazy_import_db_dependencies()
            
            # Check if we have all required dependencies for DB operations
            required_deps = ["db_query_prompt_loader", "db_query_exec", "Queries"]
            missing_deps = [dep for dep in required_deps if dep not in db_deps]
            
            if not missing_deps:
                function_name = dboconfig
                logger.info(f"Using DB-specific function name: {function_name}")
                try:
                    # Use the DB prompt loader
                    logger.info("Loading DB-specific prompts")
                    system_text, example_text, schema_text, input_tokens_count, output_tokens_count = load_db_prompts(
                        func_params, db_deps
                    )
                    combined_input_tokens_count += input_tokens_count
                    combined_output_tokens_count += output_tokens_count
                    logger.info(f"DB prompt loading complete. Input tokens: {input_tokens_count}, Output tokens: {output_tokens_count}")
                except ImportError as e:
                    logger.warning(f"Failed to load DB prompts: {e}")
                    logger.info("Falling back to standard prompt loading")
                    # Fall back to standard prompt loading
                    dboconfig = None
            else:
                logger.warning(f"Missing required DB dependencies: {missing_deps}")
                dboconfig = None
        
        # If DB config was not available or failed, load standard prompts
        if dboconfig is None:
            logger.info("Loading standard prompts")
            try:
                system_text = load_prompt_yaml(directory + r"\system_prompt.yaml")
                schema_text = load_prompt_yaml(directory + r"\schema_prompt.yaml")
                example_text = load_prompt_yaml(directory + r"\example_prompt.yaml")
                logger.info("Successfully loaded all standard prompts")
            except Exception as e:
                logger.error(f"Error loading standard prompts: {str(e)}")
                raise

        # -----------------------------------------------------------------------------
        # SECTION: Define and Create Prompt Template
        # -----------------------------------------------------------------------------
        # Create chat prompt templates from the loaded prompts
        logger.info("Creating prompt templates")
        system_prompt = ChatPromptTemplate.from_template(system_text)
        schema_prompt = ChatPromptTemplate.from_template(schema_text)
        example_prompt = ChatPromptTemplate.from_template(example_text)
        start_prompt = ChatPromptTemplate.from_template(start_text)

        standard_template = """
        ## System: {system}
        ## Schema: {schema}
        ## Example: {example}
        ## Start: {start}
        """
        standard_template = PromptTemplate.from_template(standard_template)

        # Create the template as a list of tuples
        template = [
            ("system", system_prompt),
            ("schema", schema_prompt),
            ("example", example_prompt),
            ("start", start_prompt)
        ]
        logger.info("Prompt templates created successfully")

        # -----------------------------------------------------------------------------
        # SECTION: Create Pydantic Models
        # -----------------------------------------------------------------------------
        logger.info("Preparing to create Pydantic models")
        for params in output_params:
            for key in params.keys():
                param_names.append(params[key]['value'])
                if params[key]['data_type'].lower() == 'list':
                    subparams_values, subparams_datatypes = get_subparams(params[key]['sub_params'])
                    logger.info(f"Extracted {len(subparams_values)} sub-parameters")
                    continue
                data_types.append(params[key]['data_type'])

        logger.info(f"Creating output models with {len(param_names)} parameters")
        if not subparams_values and not subparams_datatypes:
            logger.info("Creating simple GenericAgentModel without sub-parameters")
            GenericAgentModel = create_generic_output_model(
                "GenericAgentModel",
                param_names,
                data_types
            )
        
        elif isinstance(subparams_values, List):
            logger.info("Creating nested models with sub-parameters")
            GenericSubAgentModel = create_generic_output_model(
                "GenericSubAgentModel",
                subparams_values,
                subparams_datatypes,
            )
            data_types.append(List[GenericSubAgentModel])
            GenericAgentModel = create_generic_output_model(
                "GenericAgentModel",
                param_names,
                data_types
            )

        # Create a pipeline prompt template for the agent
        logger.info("Creating pipeline prompt template")
        query_prompt = PipelinePromptTemplate(
            final_prompt=standard_template,
            pipeline_prompts=template
        )

        parser = JsonOutputParser(pydantic_object=GenericAgentModel)
        logger.info("Created JSON output parser with Pydantic model")

        # Create the query chain by combining the prompt, model, and parser
        logger.info("Building query chain")
        query_chain = query_prompt | llm_config_loader() | parser

        # -----------------------------------------------------------------------------
        # SECTION: Execute the Chain
        # -----------------------------------------------------------------------------
        # Calling the LLM by passing the input parameters
        logger.info("Executing the query chain with provided parameters")
        with get_openai_callback() as cb:
            try:
                ai_response = query_chain.invoke(func_params)
                input_tokens_count = cb.prompt_tokens
                output_tokens_count = cb.completion_tokens
                logger.info(f"Query chain execution complete. Input tokens: {input_tokens_count}, Output tokens: {output_tokens_count}")
                
                print("AI Response: ", ai_response)
                
                # Handle DB-specific processing if DB config is available
                if dboconfig is not None:
                    logger.info("Processing DB-specific response")
                    db_deps = lazy_import_db_dependencies()
                    
                    if "db_query_exec" in db_deps and "Queries" in db_deps:
                        # Extract query from response
                        query = ai_response.get('ai_response', ai_response)
                        logger.info(f"Extracted query from response")
                        
                        # Add query to repository
                        try:
                            add_query_to_repository(query, db_deps)
                            logger.info("Successfully added query to repository")
                        except Exception as e:
                            logger.warning(f"Failed to add query to repository: {str(e)}")
                        
                        # Execute the query
                        try:
                            logger.info(f"Executing DB query for function: {function_name}")
                            ai_response = execute_db_query(query, function_name, db_deps)
                            logger.info("Query execution successful")
                        except ImportError as e:
                            logger.warning(f"Failed to execute DB query: {e}")
                        except Exception as e:
                            logger.error(f"Error during DB query execution: {str(e)}")
                        
                        # Parse JSON response if needed
                        if isinstance(ai_response, str):
                            try:
                                ai_response = json.loads(ai_response)
                                logger.info("Successfully parsed JSON response")
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse response as JSON: {str(e)}")
                else:
                    # Extract AI response for non-DB cases
                    logger.info("Processing standard (non-DB) response")
                    if 'ai_response' in ai_response:
                        ai_response = ai_response['ai_response']
                        logger.info("Extracted 'ai_response' field from response")
                    if isinstance(ai_response, str):
                        try:
                            ai_response = json.loads(ai_response)
                            logger.info("Successfully parsed string response as JSON")
                        except json.JSONDecodeError as e:
                            logger.info(f"Response is not JSON format: {str(e)}")
                
                combined_input_tokens_count += input_tokens_count
                combined_output_tokens_count += output_tokens_count
                logger.info(f"Final token counts - Input: {combined_input_tokens_count}, Output: {combined_output_tokens_count}")
            
            except Exception as e:
                logger.error(f"Error during query chain execution: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"Unhandled exception in generic_agent: {str(e)}")
        # Return empty response with zero token counts in case of failure
        return {}, 0, 0
        
    return ai_response, combined_input_tokens_count, combined_output_tokens_count

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------