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

        prompt="""Extract information from the resume text and format as a flat JSON with these exact fields. 
    Use 'N/A' for missing information. Do not create nested structures, lists, or dictionaries within values.
    For multiple items like projects or skills, combine them with commas in a single string.

    Required output format:
    {
        "Name": "full name as string",
        "Phone": "phone number as string",
        "Email": "email address",
        "City": "city name or N/A",
        "State": "state name or N/A",
        "University": "full university name",
        "Year_of_study": "only graduation year",
        "Course": "degree type",
        "Discipline": "field of study",
        "CGPA": "GPA value or N/A",
        "Key_Skills": "all skills separated by commas",
        "GenAI_Experience_Score": "score as 1, 2, or 3",
        "AI_ML_Experience_Score": "score as 1, 2, or 3",
        "Internships": "all internships separated by commas in Company Name(Designation) Format",
        "Projects": "all projects separated by commas only title of project ",
        "Certifications": "all certifications separated by commas",
        "Other_Achievements": "all achievements separated by commas",
        "Total_Experience": "calculate total years of experience: add up all work/internship durations, convert months to years (divide by 12), round to 1 decimal place. If experience spans multiple roles or positions, sum all durations. Example: 2 internships of 3 months each = 0.5 years because 3/12+3/12=0.5" 
    }

    Important:
    - Combine multiple items into single comma-separated strings
    - Do not use nested structures or lists
    - Keep all values as simple strings
    - Use N/A for missing information
    - For experience scores, use the scoring criteria below
    """
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




