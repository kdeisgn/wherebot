import os
from dotenv import load_dotenv
from openai import OpenAI

class LLMAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.environ['OPENAI_API_KEY']
        self.client = OpenAI()
        self.model = "gpt-5-nano"
        self.conversation_id = None
        print("[INFO] Initialized LLM Agent")

    def create_conversation(self):
        '''
            Creates a conversation ID. Conversation history is stored in conversation. (Stateful) 
            Output: conversation ID.
        '''
        if self.conversation_id:
            print("[INFO] Conversation ID exists. Skip creating one...")
            return self.conversation_id
        else:
            print("[INFO] Conversation ID do not exists. Creating one...")
            conversation = self.client.conversations.create(
                items = [
                    {
                        "type": "message",
                        "role": "developer",
                        "content": "You are Stretch from Hello Robot." ## NEED TO WRITE THE INSTRUCTIONS
                    }
                ]
            )
            self.conversation_id = conversation.id
            print(f"[INFO] Conversation ID: {self.conversation_id}")
            return self.conversation_id
    
    def create_response(self, conversation_id, prompt):
        '''
            Reply for a prompt/transcription from the LLM. It gets added back into the conversation.
            Input: conversation ID and user prompt.
            Output: LLM response.
        '''
        print("[INFO] Generating response...")
        response = self.client.responses.create(
            model = self.model,
            input = [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            conversation = conversation_id
        )
        return response.output_text

    def delete_conversation(self):
        '''
            Deletes an entire conversation.
            Input: conversation ID.
        '''
        self.client.conversations.delete(self.conversation_id)
        print("[INFO] Conversation deleted")