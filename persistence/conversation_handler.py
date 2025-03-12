import uuid
import os
import json
import logging
from persistence.dao import DataAccessObject
from persistence.schema import DatabaseSchema
from models.azure_openai_model import model
from persistence.database import DatabaseConnection
from persistence.utils.utility_functions import generate_name
 
 
# Get a logger instance for this module
logger = logging.getLogger(__name__)
 
 
class BusinessLogic:
    def __init__(self):
        db_conn = DatabaseConnection(
        host=os.getenv("POSTGRES_HOST"),
        database=os.getenv("POSTGRES_DATABASE"),
        user=os.getenv("POSTGRES_USERNAME"),
        password=os.getenv("POSTGRES_PASSWORD")
        )
        db_conn.establish_connection()
        self.db_conn = db_conn
        self.dao = DataAccessObject(db_conn)
        self.model = model
 
    
    def chat_history(self, thread_id, query, summary, input_tokens_count, output_tokens_count):
        data = self.dao.retrieve_data(thread_id)
        data_list = json.loads(data)
 
        # Extract the content as a list
        content_list = [item['content'] for item in data_list]
        max_step = 0
        if len(data_list)!=0:
            max_step = max(item['step'] for item in data_list)+1
        # print("list === > ", content_list)
        query = "HumanMessage="+query
        content_list.append(query)
        uuid2 = uuid.uuid4()
        message_id = str(uuid2)
 
        data = {
            'thread_id': thread_id,
            'message_id': message_id,
            'content': query,
            'step': max_step,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_tokens': 0,
            'feedback':" "
        }
        self.dao.insert_data(data)
        AIMessage = "AIMessage="+summary
        data = {
            'thread_id': thread_id,
            'message_id': message_id,
            'content': AIMessage,
            'step': max_step+1,
            'input_tokens': input_tokens_count,
            'output_tokens': output_tokens_count,
            'total_tokens': input_tokens_count + output_tokens_count,
            'feedback': ""
        }
        self.dao.insert_data(data)
        # return output.content
        json_object = {"thread_id": thread_id, "content": summary}
        return json.dumps(json_object)

 
    # Append Human & AI messages and insert into Messages table
    def chat_conversation(self, thread_id, ellis_response):
        try:
            user_input, summary, input_tokens_count, output_tokens_count =self.extract_summary(ellis_response)
            AIMessage = self.chat_history(thread_id, user_input, summary, input_tokens_count, output_tokens_count)
            return AIMessage
        except Exception as e:
            logger.error(f"Failed to update chat history: {e}")
            raise e
 
    # Retrieve chat history from Messages table
    def retrieve_chat_conversation(self, thread_id):
        try:
            return json.loads(self.dao.retrieve_data(thread_id))
        except Exception as e:
            logger.error(f"Failed to retrieve chat history: {e}")
            raise e
 
    # insert new chat id and email id to user table
    def insert_user_chat_history(self, email_id, user_input):
        try:
            uuid1 = uuid.uuid4()
            thread_id = str(uuid1)
            short_name = generate_name(user_input)
            data = self.dao.insert_user_chat_history(email_id, thread_id, short_name)
            return thread_id, short_name
        except Exception as e:
            logger.error(f"Failed to insert user details: {e}")
            raise e
 
    # retrieve the user chat session based on user email ID
    def retrieve_user_chat_history(self, email_id):
        try:
            data = self.dao.retrieve_user_chat_history(email_id)
            return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to retrieve user details: {e}")
            raise e
    # update user feedback
    def update_feedback(self, message_id, feedback):
        try:
            data = self.dao.update_feedback(message_id, feedback)
            return data
        except Exception as e:
            logger.error(f"Failed to update user feedback: {e}")
            raise e
    # retrieve the user conversation history based on user thread ID
    def retrieve_conversation_history(self, thread_id):
        try:
            data = self.dao.retrieve_data(thread_id)
            data_list = json.loads(data)
            # Extract the content as a list
            content_list = [item['content'] for item in data_list]
            return json.loads(json.dumps(content_list))
        except Exception as e:
            logger.error(f"Failed to retrieve user details: {e}")
            raise e

    def extract_summary(self, ellis_response):
        user_input = None
        summary = None
        input_tokens_count = ellis_response['input_tokens_count']
        output_tokens_count = ellis_response['output_tokens_count']
        for message in ellis_response['conversation']['present_conversation']:
            if 'user_input' in message:
                user_input = message['user_input']
            if'summary_agent' in message:
                if isinstance(message['summary_agent'], dict):
                    summary = message['summary_agent'].get('summary')
                else:
                    summary = message['summary_agent']
                break  # Stop searching once the summary is found
 
        return user_input, summary, input_tokens_count, output_tokens_count

    def chat_conversation_handler(self, data):
        func_name = data["func_name"]
        user_input = data.get("user_input")
        
        conversation_history = None
        thread_id = None
        short_name = ""
        chat_conversation = None
        user_chat_history = None
        feedback = None

        if func_name == "newchat":  
            email_id = data["user_details"]["user_mail"]     
            thread_id, short_name = self.insert_user_chat_history(email_id, user_input)
            conversation_history = []
        elif func_name == "chatconversation":
            thread_id = data["thread_id"]
            conversation_history = self.retrieve_conversation_history(thread_id)
        elif func_name == "retrieveconversation":
            thread_id = data["thread_id"]
            chat_conversation = self.retrieve_chat_conversation(thread_id)
        elif func_name == "chathistory":
            email_id = data["user_details"]["user_mail"]
            user_chat_history = self.retrieve_user_chat_history(email_id)
        elif func_name == "feedback":
            message_id = data["message_id"]
            feedback = data["feedback"]
            feedback = self.update_feedback(message_id, feedback)
        
        response = {
            "conversation_history": json.dumps(conversation_history) if conversation_history is not None else None,
            "thread_id": thread_id,
            "short_name": short_name,
            "chat_conversation": chat_conversation,
            "user_chat_history": user_chat_history,
            "feedback": feedback            
        }
        return json.loads(json.dumps(response))