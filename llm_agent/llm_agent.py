import json
import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI

_STRUCTURED_INSTRUCTION = (
    "You translate natural language requests for a Stretch robot into a JSON summary. "
    "Focus on what object should be found, where it was last seen (if provided), and any "
    "distinctive visual traits. Reply with JSON matching "
    '{"object": "<string>", "last_seen_location": "<string>", "traits": ["<string>", ...]}. '
    "Use empty strings or an empty list if a detail is missing. Return only JSON without commentary."
)

class LLMAgent:
    def __init__(self):
        load_dotenv()
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in environment.")
        self.client = OpenAI(api_key=api_key)
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

    def extract_object_details(self, utterance: str) -> Dict[str, Any]:
        """
        Use the LLM to summarize an utterance into object/location/traits fields.
        Returns a dict with keys object, last_seen_location, traits.
        """
        print("[INFO] Parsing object request via LLM...")
        try:
            response = self.client.responses.create(
                model=self.model,
                input=[
                    {"role": "system", "content": _STRUCTURED_INSTRUCTION},
                    {"role": "user", "content": utterance},
                ],
            )
            payload = self._extract_json(response.output_text)
        except Exception as exc:
            print(f"[ERROR] Failed to parse request with LLM: {exc}")
            payload = {}

        object_name = payload.get("object", "").strip() if isinstance(payload, dict) else ""
        location = payload.get("last_seen_location", "").strip() if isinstance(payload, dict) else ""
        traits = payload.get("traits", []) if isinstance(payload, dict) else []
        if not isinstance(traits, list):
            traits = []

        clean_traits = []
        for t in traits:
            if isinstance(t, str):
                value = t.strip()
                if value:
                    clean_traits.append(value)
        return {
            "object": object_name,
            "last_seen_location": location,
            "traits": clean_traits,
        }

    @staticmethod
    def _extract_json(raw_text: str) -> Dict[str, Any]:
        raw_text = (raw_text or "").strip()
        if not raw_text:
            return {}
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            start = raw_text.find("{")
            end = raw_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                snippet = raw_text[start : end + 1]
                try:
                    return json.loads(snippet)
                except json.JSONDecodeError:
                    pass
        return {}

    def delete_conversation(self):
        '''
            Deletes an entire conversation.
            Input: conversation ID.
        '''
        if self.conversation_id:
            self.client.conversations.delete(self.conversation_id)
            print("[INFO] Conversation deleted")
