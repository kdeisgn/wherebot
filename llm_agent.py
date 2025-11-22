import os
import json
import pyttsx3
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
                        "content": """You are Stretch from Hello Robot. Your goal is to help a user find a misplaced object in their house by gathering details \
                            about the object and its location. You will ask relevant questions one at a time and gather the information in a JSON format.\n
                            Example:
                            You: "What is the object you're looking for?"
                            User: "I can't find my phone."
                            You: "Can you describe the phone?"
                            User: "It is black in color."
                            You: "Where do you last remember seeing or using it?"
                            User: "I think I left it in my bedroom."
                            You: "Have you been to any other rooms since the phone was last seen?"
                            User: "I've been to the kitchen and then the bathroom."
                            \n
                            Output JSON:
                            {
                              "object" : {
                                "name" : "phone",
                                "description" : {"color" : "black"}
                              },
                              "last_known_location" : "bedroom",
                              "visited_rooms" : ["kitchen", "bathroom"]
                            }\n
                            After gathering necessary information, output the JSON. Keep your questions short and crisp.\n
                            Do not engage in any other form of conversation like small talk, general chat other than object-information gathering.\n
                            If the user insists or continue asking unrelated questions, say "Sorry, I don't know."
                            """
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
        output = response.output_text
        
        # If the llm response is a JSON, format it. Else return response
        try:
            json_output = json.loads(output)
            self._format_response(json_output)
            return "Thank you for the information. I'll start searching."
        except Exception as e:
            return output
    
    def _format_response(self, json_output):
        '''
            Format JSON response.
            Input: json output from the llm.
            Output: object and location details.
        '''
        print(f"[INFO] JSON output: {json_output}")
        object_name = json_output["object"]["name"]
        last_known_location = json_output["last_known_location"]
        other_known_location = ", ".join(json_output["visited_rooms"])
        print(f"[INFO] Object to search: {object_name}")
        print(f"[INFO] Top search location: {last_known_location}")
        print(f"[INFO] Other search location(s): {other_known_location}")
        ## TODO: Need to add more

    def delete_conversation(self):
        '''
            Deletes an entire conversation.
            Input: conversation ID.
        '''
        self.client.conversations.delete(self.conversation_id)
        print("[INFO] Conversation deleted")
    
    def convert_response_to_audio(self, text, fname="llm_audio.wav"):
        '''
            Converts llm response (text string) into audio (.wav) so I can play it on Stretch's speakers using play_audio().
            Input: text (string. llm's response) and file name.
            Output: None (Audio file is saved).
        '''
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.save_to_file(text, fname)
            engine.runAndWait()
            print("[INFO] LLM response converted to Audio")
        except Exception as e:
            print(f"[ERROR] LLM response to Audio conversion failed: {e}")