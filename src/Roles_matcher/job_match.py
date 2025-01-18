from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import spacy
import numpy as np
from typing import Dict, List
import json
import re
import os

class ResumeMatcher:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.vectorizer = TfidfVectorizer(stop_words='english')
        # self.jobs = self._load_jobs()
        self.jobs = self._load_jobs()
        self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        
        self.categories = {
            'skills': 0.4,
            'experience': 0.3,
            'education': 0.2,
            'projects': 0.1
        }
    def _load_jobs(self) -> Dict:
        """Load jobs from JSON file"""
        try:
            # Get the directory containing job_match.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            json_path = os.path.join(current_dir, 'sample2.json')
            
            # Check if file exists
            if not os.path.exists(json_path):
                print("path not found")
                # Create sample jobs if file doesn't exist
                sample_jobs = {
                    "jobs": {
                        "ml_engineer": {
                            "title": "ML Engineer",
                            "description": "Looking for ML engineer with Python and TensorFlow experience",
                            "required_skills": ["Python", "TensorFlow", "ML"],
                            "experience": "2+ years"
                        },
                        "data_scientist": {
                            "title": "Data Scientist",
                            "description": "Need data scientist with ML and analytics background",
                            "required_skills": ["Python", "Statistics", "ML"],
                            "experience": "3+ years"
                        }
                    }
                }
                
                # Write sample jobs to file
                with open(json_path, 'w') as f:
                    json.dump(sample_jobs, f, indent=4)
            
            # Load jobs from file
            with open(json_path, 'r') as f:
                return json.load(f)['jobs']
                
        except Exception as e:
            print(f"Error loading jobs: {e}")
            return {}
        # try:
            
        #     with open(os.path.join(os.getcwd(),'src\\Roles_matcher\\sample2.json'), 'r') as f:
        #         return json.load(f)['jobs']
        # except Exception as e:
        #     print(f"Error loading jobs: {e}")
        #     return {}
    def match_resume(self, orig_text:str,resume_data: Dict) -> List[Dict]:
        """Match resume against all jobs and return top 3 matches"""
        matches = []
        
        for job_id, job in self.jobs.items():
            job_des=""
            for x in job:
                if isinstance(job[x],list):
                    t="".join(job[x])
                    
                elif isinstance(job[x],dict):
                    t="".join(list(str(job[x].values())))
                else:
                    t=str(job[x])
                job_des+=t+" "
            
            score = self._calculate_match(resume_data,orig_text, job_des)
            
            matches.append({
                'job_title': job['title'],
                'match_score': score,
                'skills_match': self._extract_matching_skills(resume_data, job_des),
                'missing_skills': self._extract_missing_skills(resume_data, job_des),
                'experience_match': self._check_experience_match(resume_data, job_des)
            })
        
        # Sort by match score and return top 3
        return sorted(matches, key=lambda x: x['match_score']['overall_match'], reverse=True)[:3]

    def _calculate_match(self, resume_fields: dict, original_resume_text:str,job_description: str) -> dict:
        """Calculate match score between resume and job description"""
        
        # Prepare resume text by combining relevant fields
        resume_text = ' '.join([
            ' '.join(resume_fields.get('key_skills', [])),
            resume_fields.get('Internships', ''),
            resume_fields.get('project', ''),
            resume_fields.get('Supporting_Info', '')
        ])
        

        # Calculate similarity scores
        resume_text+=original_resume_text
        resume_text = self._preprocess_text(resume_text)
        job_description = self._preprocess_text(job_description)
        similarity = self._get_similarity_score(resume_text, job_description)
        
        keyword_match = self._get_keyword_match(resume_text, job_description)
        
        # Calculate final score
        match_score = (similarity * 0.6) + (keyword_match * 0.4)
        
        return {
            'overall_match': round(match_score * 100, 2),
            'similarity_score': round(similarity * 100, 2),
            'keyword_match': round(keyword_match * 100, 2),
            'analysis': self._get_detailed_analysis(resume_fields, job_description)
        }

    def _get_similarity_score(self, resume_text: str, job_description: str) -> float:
        """Calculate cosine similarity between resume and job description"""
      
        try:
              # Generate embeddings
            resume_embedding = self.model.encode(resume_text, convert_to_tensor=True)
            job_embedding = self.model.encode(job_description, convert_to_tensor=True)
            
            # Calculate cosine similarity
            similarity = util.pytorch_cos_sim(resume_embedding, job_embedding)
            return similarity.item()
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text by removing stop words, punctuation, and performing lemmatization"""
        doc = self.nlp(text.lower())
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return ' '.join(tokens)

    def _get_keyword_match(self, resume_text: str, job_description) -> float:
        """Calculate keyword matching score"""
        # Extract keywords from job description
        job_doc = self.nlp(str(job_description))
        job_keywords = set([token.text.lower() for token in job_doc if token.pos_ in ['NOUN', 'PROPN']])
        
        # Extract keywords from resume
        resume_doc = self.nlp(resume_text)
        resume_keywords = set([token.text.lower() for token in resume_doc if token.pos_ in ['NOUN', 'PROPN']])
        
        # Calculate match
        matched_keywords = job_keywords.intersection(resume_keywords)
        return len(matched_keywords) / len(job_keywords) if job_keywords else 0.0

    def _get_detailed_analysis(self, resume_fields: dict, job_description: str) -> dict:
        """Generate detailed analysis of match"""
        return {
            'matching_skills': self._extract_matching_skills(resume_fields, job_description),
            'missing_skills': self._extract_missing_skills(resume_fields, job_description),
            'experience_match': self._analyze_experience_match(resume_fields, job_description)
        }

    def _extract_matching_skills(self, resume_fields: dict, job_description: str) -> list:
        """Extract matching skills between resume and job description"""
        job_doc = self.nlp(str(job_description).lower())
        resume_skills = set(skill.lower() for skill in resume_fields.get('key_skills', []))
        
        return list(skill for skill in resume_skills 
                   if any(token.text.lower() == skill for token in job_doc))

    def _extract_missing_skills(self, resume_fields: dict, job_description: str) -> list:
        """Extract skills mentioned in job description but missing in resume"""
        job_doc = self.nlp(str(job_description).lower())
        resume_skills = set(skill.lower() for skill in resume_fields.get('key_skills', []))
        
        return list(token.text for token in job_doc 
                   if token.pos_ == 'NOUN' and token.text.lower() not in resume_skills)
    
    def _check_experience_match(self, resume: Dict, job: Dict) -> bool:
        try:
            resume_exp = float(resume.get('Total_experience', '0').split()[0])
            required_exp = float(job['experience'].split('+')[0])
            return resume_exp >= required_exp
        except:
            return False
    def _extract_required_experience(self, job_description: str) -> float:
        """
        Extract required years of experience from job description
        Returns float value of years required
        """
        try:
            # Common patterns for experience requirements
            patterns = [
                r'(\d+)\+?\s*(?:years?|yrs?)',  # matches "5+ years", "3 yrs"
                r'(\d+)-(\d+)\s*(?:years?|yrs?)',  # matches "3-5 years"
                r'minimum\s*(?:of\s*)?(\d+)',  # matches "minimum of 3"
                r'at\s*least\s*(\d+)',  # matches "at least 5"
            ]
            
            text = str(job_description).lower()
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    # If range (e.g., 3-5 years), take lower bound
                    return float(match.group(1))
                    
            # Default to 0 if no experience mentioned
            return 0.0
            
        except Exception as e:
            print(f"Error extracting experience: {e}")
            return 0.0

    def _analyze_experience_match(self, resume_fields: dict, job_description: str) -> dict:
        """Analyze experience level match"""
        experience = resume_fields.get('Total_experience', '0')
        try:
            exp_years = float(experience.split()[0])
            required_exp = self._extract_required_experience(job_description)
            return {
                'has_required_experience': exp_years >= required_exp,
                'years_difference': exp_years - required_exp
            }
        except:
            return {'has_required_experience': False, 'years_difference': 0}
if __name__ == "__main__":
    def test_matcher():
        # Sample resume data
        resume_text = """
        Experienced ML Engineer with 3 years in Python, TensorFlow, and AWS.
        Developed multiple machine learning models and deployed to production.
        Strong experience in data analysis and model optimization.
        """
        
        resume_fields = {
            'key_skills': ['Python', 'TensorFlow', 'AWS', 'Machine Learning', 'Docker'],
            'Total_experience': '3 years',
            'genai_score': 2,
            'aiml_score': 2
        }
        
        # Create matcher instance
        matcher = ResumeMatcher()
        
        # Get matches
        matches = matcher.match_resume(resume_text, resume_fields)
        
        # Print results
        print("\nTest Results:")
        print("-------------")
        for match in matches:
            print(f"\nJob: {match['job_title']}")
            print(f"Match Score: {match['match_score']}")
            print(f"Missing Skills: {match['missing_skills']}")
    test_matcher()