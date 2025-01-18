import google.generativeai as genai
import openai
import json
import os
from dotenv import  load_dotenv
from abc import ABC, abstractmethod


class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""
    @abstractmethod
    def query(self, prompt: str) -> str:
        pass

class GeminiLLM(BaseLLM):
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(os.getenv('GEMINI_MODEL'))

    def query(self, prompt: str) :
        try:
            response = self.model.generate_content(prompt+ " Return only valid JSON, no other text.")
            cleaned_text=response.text.replace("json",'')
            cleaned_text=cleaned_text.replace("```",'"""')
            start = cleaned_text.find('{')
            end = cleaned_text.rfind('}') + 1
            json_str = cleaned_text[start:end]
            return json_str

        except Exception as e:
            print(f"Gemini API error: {e}")
            raise

class OpenAILLM(BaseLLM):
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        openai.api_key = api_key
        self.model = "OPENAI_MODEL"

    def query(self, prompt: str) -> str:
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                     {"role": "system", "content": "You are a resume parsing assistant."},{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format='json'

            )
            return response.choices[0].message['content']
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
class AzureOpenAI(BaseLLM):
    def __init__(self):
        self.url=os.getenv('AZURE_OPENAI_ENDPOINT')
        self.model=os.getenv('AZURE_OPENAI_MODEL')
        self.api_key=os.getenv('AZURE_OPENAI_API_KEY')
    
    def query(self,prompt:str)->str:
        try:
            import requests
            headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }
            response = requests.post(self.url,headers=headers, json=
               { "model":self.model,
                "messages":[
                     {"role": "system", "content": "You are a resume parsing assistant."},{"role": "user", "content": prompt}],
                "temperature":0.3,
                "response_format":'json'

            })
            print(response)
            return response.choices[0].message['content']
        except Exception as e:
            print(f"AZURE OpenAI API error: {e}")
            raise




def get_llm_model() -> BaseLLM:
    """Factory method to get LLM instance"""
    load_dotenv()
    

    try:
        if os.getenv('GEMINI_API_KEY'):
            return GeminiLLM()
    except Exception as e:
        print(f"Failed to initialize Gemini: {e}")
    
    try:
        if os.getenv('AZURE_OPENAI_API_KEY'):
            return AzureOpenAI()
    except Exception as e:
        print(f"Failed to initialize Azure  OpenAI: {e}")

    try:
        if os.getenv('OPENAI_API_KEY'):
            return OpenAILLM()
    except Exception as e:
        print(f"Failed to initialize OpenAI: {e}")
        
    raise RuntimeError("No LLM configuration available")




# Stilll need to be corrected
