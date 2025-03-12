"""
Module Name: flask_api_validations.py

Description:

This module contains functions for validating API requests and request IDs for a Flask application. 

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import json

# Third-party imports
from flask import jsonify

# -----------------------------------------------------------------------------
# SECTION: ask-ellis api validations
# -----------------------------------------------------------------------------

def validate_ask_ellis_api_request_data(data):
    """
    Validate the request data for the ask-ellis API.

    Args:
        data (dict): The request data to validate.

    Returns:
        Response: JSON response with an error message and HTTP status code if validation fails.
        None: If validation passes.
    """
    if not data:
        return jsonify({"error": "Missing request body"}), 400

    # if 'request_id' not in data:
    #     return jsonify({"error": "Missing required parameter: request_id"}), 400

    if 'user_input' not in data:
        return jsonify({"error": "Missing required parameter: user_input"}), 400

    if 'user_details' not in data:
        return jsonify({"error": "Missing required parameter: user_details"}), 400

    return None  # No errors

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------