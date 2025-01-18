import re
import json
from llm_config.llm_conf import get_llm_model

class FieldExtractor:
    """
    It represents a Field Extractor 
    Methods: 
        extract_field () : Return JSON response based on LLM response carrying all fields data
        _parse_response():Return a dict data structure from string JSON Input 
    """
    

    def __init__(self):
        """It initialize a llm model"""
        self.llm_model=get_llm_model()
    
    def get_scoring_prompt(self):
        """For Generating Scores"""
        return """ Give score based on Analyzsis of  the resume information and assign scores (1-3) for GenAI and AI/ML experience:

    Scoring Criteria:
    1 (Exposed) = Basic knowledge, used tools, theoretical understanding
    2 (Hands-on) = Project implementation, practical experience, tool proficiency
    3 (Advanced) = Complex implementations, research work, framework development, production deployments

    For GenAI:
    - Score 1: Basic LLM usage, simple prompting
    - Score 2: Prompt engineering, LangChain/LlamaIndex usage, embeddings
    - Score 3: Agentic RAG, evaluation frameworks, custom agent development

    For AI/ML:
    - Score 1: Basic ML concepts, simple models
    - Score 2: Deep learning projects, model deployment, MLOps
    - Score 3: Custom architectures, research papers, distributed training"""
        

    def extract_fields(self,resume_text):

        prompt="""Extract the following information from the resume text if no available then write N/A and response must be in JSON Format
        {
        "Name":"",
    
        "Phone":"",
        "Email":""
        "City":"",
        "State":"",
        "University":"",
        "Year_of_study":"",
        "Course":"",
        "Discipline":"",
        "CGPA": "",
        "Key_Skills": ,"
        "GenAI_Experience_Score": "",
        "AI_ML_Experience_Score": "",
     
        "Internships":"",
        "Projects":""
        "Certifications":""
        "Other_Achievements":""
        "Total_Experience":"in years only"
        }"""
        prompt+= self.get_scoring_prompt() + f"Resume text:\n      {resume_text}    "

        try:
            # print(prompt)
            response=self.llm_model.query(prompt)
            print(response)
            return  self._parse_response(response)
        except Exception as e:
            print(f"Error in LLM extraction:{e}")
            return {}
    def _parse_response(self,response):
        
        try:
            cleaned_response=response.strip()
            if isinstance(cleaned_response,str):
                return json.loads(cleaned_response)
            return cleaned_response
                # return cleaned_response.json()
        except Exception as e:
            print(f"Error in parsing the LLM response:{e}")
            return {}




