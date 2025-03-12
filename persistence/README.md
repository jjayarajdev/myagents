API Documentation

1. Business logic object

    business_logic = BusinessLogic()

2. New Chat
API Call: business_logic.insert_user_chat_history(email_id, user_input)
Description: Inserts a new chat history entry for a user, creating a record of the conversation. This API call is triggered when a new chat is initiated, and it stores the user's email ID, thread ID, and short name.
Parameters:
email_id: User's email ID
thread_id: Unique thread ID
short_name: User's short name
Returns: thread_id, short_name

3. update Conversation History
API Call: business_logic.chat_conversation(thread_id, user_input)
Description: update the conversation history for a given thread ID, providing a record of all messages exchanged in the conversation. This API call is used to update the conversation history to the user.
Parameters:
thread_id: Unique thread ID
user input: 
Returns: none

4. Retrieve Chat Conversation
API Call: business_logic.retrieve_chat_conversation(thread_id)
Description: Retrieves the chat conversation for a given thread ID, including all messages and their corresponding data. This API call is used to display the chat conversation to the user.
Parameters:
thread_id: Unique thread ID
Returns: Chat conversation data

5. Retrieve User Chat History
API Call: business_logic.retrieve_user_chat_history(email_id)
Description: Retrieves the chat history for a given user, providing a record of all conversations initiated by the user. This API call is used to display the user's chat history.
Parameters:
email_id: User's email ID
Returns: User's chat sessions data

6. update Feedback
API Call: business_logic.update_feedback(message_id, feedback)
Description: Updates the feedback for a given message ID, allowing users to provide feedback on the conversation. This API call stores the user's feedback and associates it with the corresponding message ID.
Parameters:
message_id: Unique message ID
feedback: User's feedback
Returns: None


Input object structure

-- New Chat
{
    "user_input": "",  ---- required field
    "func_name": "newchat",
    "user_details": {
        "country": "",
        "country_code": "",
        "market": "",
        "sector": "",
        "user_id": "",
        "user_mail": "",  ---- required field
        "user_name": " "
    }
}

-- update chat conversation
{
    "user_input": "", ---- required field
    "func_name": "chatconversation",
    "thread_id": "", ---- required field
    "user_details": {
        "country": "",
        "country_code": "",
        "market": "",
        "sector": "",
        "user_id": "",
        "user_mail": "",
        "user_name": " "
    }
}

-- retrieve Chat Conversation
{
    "func_name": "retrieveconversation",
    "thread_id": "", - required field  
}

-- Retrieve user chat sessions
{
    "func_name": "chathistory",
    "user_details": {
        "user_mail": ""  --- required field
    }
}

-- update Feedback

{
    "func_name": "feedback",
    "message_id":"",  --- required field
    "feedback":""  ---- required field
}


