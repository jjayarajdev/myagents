import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    POSTGRES_HOST = os.getenv('POSTGRES_HOST')
    POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')