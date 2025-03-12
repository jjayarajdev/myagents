from persistence.database import DatabaseConnection
from persistence.schema import DatabaseSchema
import json


class DataAccessObject:
    def __init__(self, db_conn):
        self.db_conn = db_conn
        self.schema = DatabaseSchema(db_conn)

    def insert_data(self, data):
        query = """
            INSERT INTO MESSAGES (THREAD_ID, MESSAGE_ID, CONTENT, STEP, INPUT_TOKENS, OUTPUT_TOKENS, TOTAL_TOKENS, FEEDBACK)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            data['thread_id'],
            data['message_id'],
            data['content'],
            data['step'],
            data['input_tokens'],
            data['output_tokens'],
            data['total_tokens'],
            data['feedback']
        )
        self.db_conn.execute_query(query, params)

    def retrieve_data(self, thread_id):
        query = "SELECT message_id, content, step FROM MESSAGES WHERE messages.thread_id =%s;"
        params = (thread_id,)
        rows = self.db_conn.fetch_data(query, params)
        content_list = [{"message_id": row[0], "content": row[1], "step": row[2]} for row in rows]
        return json.dumps(content_list, indent=4)


    def insert_user_chat_history(self, email_id, thread_id, short_name):
        query = """
            INSERT INTO USER_CHAT_HISTORY (email_id, thread_id, short_name)
            VALUES (%s, %s, %s)
        """
        params = (email_id, thread_id, short_name)
        self.db_conn.execute_query(query, params)

    def retrieve_user_chat_history(self, email_id):
        query = "SELECT THREAD_ID, SHORT_NAME FROM USER_CHAT_HISTORY WHERE USER_CHAT_HISTORY.EMAIL_ID=%s;"
        params = (email_id,)
        rows = self.db_conn.fetch_data(query, params)
        content_list = [{"thread_id": row[0], "short_name": row[1]} for row in rows]
        return json.dumps(content_list, indent=4)

    def update_feedback(self, message_id, feedback):
        
        query = """
            UPDATE messages
            SET feedback = %s
            WHERE message_id = %s
        """
        params = (feedback, message_id)
        result = self.db_conn.execute_query(query, params)
        return json.dumps(result)
    
