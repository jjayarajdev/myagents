"""
Module Name: azure_openai_model.py

Description:
This module initializes and configures the Azure OpenAI model using environment variables. 
It sets up the necessary API credentials, deployment parameters, and model configuration, 
such as temperature for output generation. The module leverages the `AzureChatOpenAI` class 
from the `langchain_openai` library to interact with the Azure OpenAI service.

"""

# -----------------------------------------------------------------------------
# SECTION: Imports
# -----------------------------------------------------------------------------

# Standard library imports
import os

# Third-party imports
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# -----------------------------------------------------------------------------
# SECTION: Environment Setup
# -----------------------------------------------------------------------------

# Load environment variables from .env file
load_dotenv()

# -----------------------------------------------------------------------------
# SECTION: Constants
# -----------------------------------------------------------------------------

# Temperature for model output; controls the creativity of the generated text
TEMPERATURE = 0.1

# -----------------------------------------------------------------------------
# SECTION: Model Initialization
# -----------------------------------------------------------------------------

# Initialize Azure OpenAI model with the necessary configuration parameters
model = AzureChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),  # API key for OpenAI from environment variables
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),  # API version for OpenAI from environment variables
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # Azure endpoint URL for OpenAI from environment variables
    azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),  # Azure deployment name from environment variables
    temperature=TEMPERATURE  # Set temperature for the model output
)

# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------