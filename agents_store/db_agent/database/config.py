# src/config.py

import os
from dotenv import load_dotenv




class SnowflakeConfig:
     # Load environment variables from .env file
    load_dotenv()
    @staticmethod
    def load():

        connection_params = {}
        connection_params['user'] = os.getenv("SF_USER")
        connection_params['password'] = os.getenv("SF_PASSWORD")
        connection_params['account'] = os.getenv("SF_ACCOUNT")
        connection_params['database'] = os.getenv("SF_DATABASE")
        connection_params['warehouse'] = os.getenv("SF_WAREHOUSE")
        connection_params['role'] = os.getenv("SF_ROLE")
        return connection_params

class PostgresConfig:
    @staticmethod
    def load():
        
        connection_params = {}
        connection_params['host'] = os.getenv('host')
        connection_params['port'] = os.getenv('port', 5432)
        connection_params['database'] = os.getenv('database', '')
        connection_params['user'] = os.getenv('user', '')
        connection_params['password'] = os.getenv('password', '')
        return connection_params


