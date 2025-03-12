"""
Module Name: flask_app.py

Description: This module sets up a Flask application to expose API endpoints.

Available Endpoints:
  
1. /get-static-user-questions [GET]
   - Fetches a static list of user questions for display on the frontend.
 
2. /ask-ellis [POST]
   - Handles the Ask Ellis workflow, processing user input and generating responses.
 
"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import logging
import os
import yaml
import uuid
import json

# Third-party imports
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

# Local application imports
# from static.static_user_queries_handler import get_static_user_questions_list, is_user_input_in_static_queries, execute_static_query_for_user_input 
from agent_config_utils.agent_app_config import agent_config, agents_list, enable_disable_agent_handler, generate_yaml_db_query_agent, get_user_config_agent, load_config, save_config, summary_agent_handler, supervisor_agent_handler, supervisor_functions_config_v1, table_pruning_prompt_handler
from agents_store.db_agent.utils.query_repository import Queries
from utils.flask_api_validations import validate_ask_ellis_api_request_data
from workflows.core_engine_workflow_graph import ask_ellis_workflow_graph
import utils.logger_config
from persistence.database import DatabaseConnection
from persistence.utils.utility_functions import generate_name
from persistence.conversation_handler import BusinessLogic
from access_controller.access_handler import AccessHandler

# -----------------------------------------------------------------------------
# SECTION: Application Initialization and Configuration
# -----------------------------------------------------------------------------

# Initialize Flask app and load environment variables
app = Flask(__name__)
CORS(app)
load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
EXP_TIME = int(os.getenv("TOKEN_EXPIRY_SECONDS", "3600"))

app.config['SECRET_KEY'] = SECRET_KEY
app.config['TOKEN_EXPIRY_SECONDS'] = EXP_TIME

# -----------------------------------------------------------------------------
# SECTION: Logger Setup
# -----------------------------------------------------------------------------

# Get a logger instance for this module
logger = logging.getLogger('werkzeug')

# -----------------------------------------------------------------------------
# SECTION: Ask Ellis Workflow Endpoint
# -----------------------------------------------------------------------------

@app.route('/ask-ellis', methods=['POST'])
def ask_ellis():
    """
    API endpoint for the Ask Ellis workflow.
    """
    try:
        Queries.query = []
        # Parse request body
        data = request.get_json()   
        business_logic = BusinessLogic()
        # func_name = ""

        # Validate request data
        validation_error = validate_ask_ellis_api_request_data(data)
        if validation_error:
            return validation_error

        # Extract required fields from API request body
        user_input = data.get("user_input")
        user_details = data.get("user_details")
        user = user_details.get("user_name")
        logger.info(f"rca_user_input: {user_input}")
        
        resp = business_logic.chat_conversation_handler(data)
        thread_id = resp["thread_id"]
        conversation_history = resp["conversation_history"]

        print("rca_user_input: ", user_input)
       
        # Call the Ask Ellis workflow
        ellis_response = ask_ellis_workflow_graph(user_input, conversation_history, user_details,user)
        resp = business_logic.chat_conversation(thread_id, ellis_response)
        return jsonify(ellis_response), 200

    except Exception as error:
        logger.error(error)
        return jsonify({
            "error": "An error occurred while processing the request.",
            "details": str(error)
        }), 500


@app.route('/conv-history', methods=['POST'])
def conv_history():
    """
    Handles RCA bot API requests.

    :return: User details or error response
    """
    try:
        # Extract JSON data from the request body
        data = request.get_json()     
        business_logic = BusinessLogic()
         
        return business_logic.chat_conversation_handler(data), 200

    except Exception as e:
        # Log the error with a more detailed message
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "An error occurred while processing the request.",
            "details": str(e)
        }), 500

@app.route('/user-login', methods=['POST'])
def user_login():
    """
    Handles RCA bot API requests.

    :return: User details or error response
    """
    try:
        # Extract JSON data from the request body
        data = request.get_json()     
        user_access = AccessHandler()         
        return user_access.execute(data), 200
    
    except Exception as e:
        # Log the error with a more detailed message
        # logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "An error occurred while processing the request.",
            "details": str(e)
        }), 500


@app.route("/agents_list", methods=["GET"])
def list_agents():
    """
    Lists all agents in the system.

    Returns:
        tuple: A tuple containing:
            - A JSON response with the list of agents (200 OK)
            - Or a JSON error message (500 Internal Server Error) if an exception occurs
    """
    try:
        agents=agents_list()
        return jsonify(agents), 200
    except Exception as error:
        logger.error(error)
        return jsonify({"error": "An error occurred while fetching agent list."}), 500


@app.route('/enable_disable_agent', methods=['POST'])
def enable_disable_agent():
    """
    Enable or disable a specified agent.
    This endpoint processes JSON requests to enable or disable a particular agent in the system.
    Args:
        None (parameters are extracted from the request JSON)
    Returns:
        tuple: JSON response and HTTP status code
            - On success: {"message": "{agent_name} enabled/disabled successfully"}, 200
            - On error: {"error": "An error occurred while enabling/disabling agent."}, 500
    Required JSON Payload:
        agent_name (str): The name of the agent to enable or disable
        enable (bool): True to enable the agent, False to disable it
        user (str): The user requesting the change
    Raises:
        Exception: Any exception that occurs during the process will be caught, logged,
                  and a 500 error response will be returned
    """
    try:
        agent_name = request.json.get('agent_name')
        enable = request.json.get('enable')
        user = request.json.get('user')
        enable_disable_agent_handler(agent_name, enable,user)
        return jsonify({"message": f"{agent_name} enabled/disabled successfully"}), 200
    except Exception as error:
        logger.error(error)
        return jsonify({"error": "An error occurred while enabling/disabling agent."}), 500


@app.route('/configure-agent', methods=['POST'])
def configure_agent():
    """
        Route that handles configuration of various agents in the system.
        This endpoint receives agent configuration data via POST request and processes it based on the
        agent type (db_agent, summary_agent, or supervisor_agent).
        Parameters:
        ----------
            None directly in function signature, but extracts from request.json:
                user (str): User identifier associated with the configuration
                agent_name (str): Name of the agent to configure ('db_agent', 'summary_agent', 'supervisor_agent')
                config_data (dict): Configuration parameters for the specified agent
        Returns:
        -------
            JSON response with message on success (200) or error details (500)

        Notes:
        -----
            - For 'db_agent', calls multiple setup functions:
                - save_config(): Persists configuration data
                - supervisor_functions_config_v1(): Sets up supervisor functions
                - table_pruning_prompt_handler(): Handles table pruning
                - generate_yaml_db_query_agent(): Creates YAML configuration
            - For 'summary_agent', calls:
                - save_config(): Persists configuration data
                - summary_agent_handler(): Processes summary agent setup
            - For 'supervisor_agent', calls:
                - save_config(): Persists configuration data
                - supervisor_agent_handler(): Handles supervisor agent setup
    """
    try:
        user = request.json.get('user')
        agent_name = request.json.get('agent_name')
        config_data = request.json.get('config_data')
        if agent_name =='db_agent': 
            save_config(config_data,agent_name,user)
            supervisor_functions_config_v1(config_data,user)
            table_pruning_prompt_handler(config_data,user)
            generate_yaml_db_query_agent(config_data,user)

        elif agent_name=='summary_agent':
            save_config(config_data,agent_name,user)
            summary_agent_handler(config_data,user)
            
        elif agent_name=='supervisor_agent':
            save_config(config_data,agent_name,user)
            supervisor_agent_handler(config_data,user)
        return jsonify({"message": "Agent configured successfully"})
    except Exception as error:
        print(error)
        logger.error(error)
        return jsonify({"error": "An error occurred while configuring agent."}), 500


@app.route('/fetch_agent_config', methods=['GET'])
def fetch_agent_config():
    """
    Fetches agent configuration based on provided agent name from query parameters.
    
    This endpoint accepts a GET request with 'agent_name' as a query parameter,
    retrieves the corresponding configuration using the agent_config function,
    and returns it as a JSON response.
    
    Returns:
        JSON response containing agent configuration data on success,
                        or an error message with 500 status code on failure.
    Raises:
        Exception: Logs any errors that occur during configuration retrieval.
    """
    try:
        agent_name = request.args.get('agent_name')
        config_data = agent_config(agent_name)
        return jsonify(config_data)
    except Exception as error:
        logger.error(error)
        return jsonify({"error": "An error occurred while fetching agent configuration."}), 500

# -----------------------------------------------------------------------------
# SECTION: Application Entry Point
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    #app.run(debug=False, host='0.0.0.0', port=5000)
    logger.setLevel(logging.ERROR)
    app.run(debug=False, host='0.0.0.0', port=5000)

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------