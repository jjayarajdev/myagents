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
import yaml
from agents_store.graph_summary_agent.utils.helper_functions import load_yaml
# -----------------------------------------------------------------------------
# SECTION: Environment Setup
# -----------------------------------------------------------------------------

# Load environment variables from .env file
load_dotenv()


def get_deployment_name_and_version(yaml_data):
    deployment_name = yaml_data['model']['deployment_name']
    version = yaml_data['model']['version']
    temperature = yaml_data['model']['temperature']
    return deployment_name, version,temperature


# -----------------------------------------------------------------------------
# SECTION: Model Initialization
# -----------------------------------------------------------------------------

# Initialize Azure OpenAI model with the necessary configuration parameters
def llm_model(deployment_name,version,temperature):
    """
    Initialize the Azure OpenAI model with the necessary configuration parameters.
    """
    model = AzureChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),  # API key for OpenAI from environment variables
        openai_api_version=version,  # API version for OpenAI from environment variables
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),  # Azure endpoint URL for OpenAI from environment variables
        azure_deployment=deployment_name,  # Azure deployment name from environment variables
        temperature= temperature  # Set temperature for the model output
    )
    return model


def llm_config_loader():
    print(os.getcwd())
    file_path = os.path.join(os.getcwd(),r'agents_store\graph_summary_agent\models\openai\openai_config.yaml')
    yaml_data = load_yaml(file_path)

    # Get the deployment name and version
    deployment_name, version ,temperature= get_deployment_name_and_version(yaml_data)
    model = llm_model(deployment_name,version,temperature)
    return model





# -----------------------------------------------------------------------------
# END OF MODULE
# -----------------------------------------------------------------------------
