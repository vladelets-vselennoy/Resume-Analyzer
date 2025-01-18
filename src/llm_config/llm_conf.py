import google.generativeai as genai
import openai
import json
import os
from dotenv import  load_dotenv
from abc import ABC, abstractmethod
import base64
from openai import AzureOpenAI  


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

# This is not Tested

# class OpenAILLM(BaseLLM):
#     def __init__(self):
#         api_key = os.getenv('OPENAI_API_KEY')
#         if not api_key:
#             raise ValueError("OPENAI_API_KEY not found in environment variables")
        
#         openai.api_key = api_key
#         self.model = "OPENAI_MODEL"

#     def query(self, prompt: str) -> str:
#         try:
#             response = openai.ChatCompletion.create(
#                 model=self.model,
#                 messages=[
#                      {"role": "system", "content": "You are a resume parsing assistant."},{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 response_format='json'

#             )
#             return response.choices[0].message['content']
#         except Exception as e:
#             print(f"OpenAI API error: {e}")
#             raise
    
class AzureOpenAILLM(BaseLLM):
    def __init__(self):
        self.endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment =os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        self.subscription_key=os.getenv('AZURE_OPENAI_API_KEY')
        self.api_version=os.getenv("Azure_openAI_API_VERSION","2024-05-01-preview")

    
    def query(self,prompt:str)->str:
        try:
            # Initialize Azure OpenAI Service client with key-based authentication    
            client = AzureOpenAI(  
                azure_endpoint=self.endpoint,  
                api_key=self.subscription_key,  
                api_version=self.api_version,
            )

            response = client.chat.completions.create(
            model=self.deployment,
            messages=[
                    {"role": "system", "content": "You are a resume parsing assistant."},{"role": "user", "content": prompt}],
            temperature=0.3,

        )
            
            # Handle response correctly
            if hasattr(response, 'choices') and len(response.choices) > 0:
                content = response.choices[0].message.content
                try:
                    # Attempt to parse JSON
                    import json
                    json_content = json.loads(content)
                    return json.dumps(json_content, indent=2)
                except json.JSONDecodeError:
                    return content
            return ""
           
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
            return AzureOpenAILLM()
    except Exception as e:
        print(f"Failed to initialize Azure  OpenAI: {e}")

    # try:
    #     if os.getenv('OPENAI_API_KEY'):
    #         return OpenAILLM()
    # except Exception as e:
    #     print(f"Failed to initialize OpenAI: {e}")
        
    raise RuntimeError("No LLM configuration available")




# Stilll need to be corrected
