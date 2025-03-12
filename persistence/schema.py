from persistence.database import DatabaseConnection

class DatabaseSchema:
    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS MESSAGES (
                THREAD_ID VARCHAR(255) NOT NULL,
                MESSAGE_ID VARCHAR(255) NOT NULL,
                CONTENT TEXT,
                STEP int4,
                INPUT_TOKENS int4,
                OUTPUT_TOKENS int4,
                TOTAL_TOKENS int4,
                FEEDBACK VARCHAR(255)            
            );
        """
        self.db_conn.execute_query(query)

    def create_user_chat_history_table(self):
        query = """
            CREATE TABLE IF NOT EXISTS USER_CHAT_HISTORY (
                EMAIL_ID VARCHAR(255),
                THREAD_ID VARCHAR(255) NOT NULL UNIQUE,
                SHORT_NAME VARCHAR(255),
                SENT_AT TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """
        self.db_conn.execute_query(query)