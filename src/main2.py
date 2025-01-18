import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from parsers.pdf_parser import PDFParser
from extractors.field_extractor import FieldExtractor
from google_drive_files.download_pdf import download_pdfs_from_folder
from Roles_matcher.job_match import ResumeMatcher
# from extractors.score_calculator import ScoreCalculator
from utils.excel_writer import ExcelWriter
class ResumeAnalyzer:
    def __init__(self):
        self.parser = PDFParser()
        self.extractor = FieldExtractor()
        self.writer = ExcelWriter()
        logging.basicConfig(level=logging.INFO)
        self.job_matcher = ResumeMatcher()
        self.logger = logging.getLogger(__name__)

    def process_single_resume(self, pdf_path: str):
        """Process a single resume"""
        try:
            self.logger.info(f"Processing resume: {pdf_path}")
            
            # Extract text from PDF
            text = self.parser.extract_text_from_pdf(pdf_path)
            if not text:
                self.logger.error(f"No text extracted from {pdf_path}")
                return {}
            
            self.logger.info(f"Text extracted successfully from {pdf_path}")
            
            # Extract fields using LLM
            fields = self.extractor.extract_fields(text)
            if not fields:
                self.logger.error("Field extraction failed")
                return {}
                
            # adding top 3 jobs
            job_matches=self.job_matcher.match_resume(text,fields)
            print("\n\n\n\n\n" ,job_matches)
            fields["Matched_Jobs"]=""

            for match in job_matches:
                fields["Matched_Jobs"]+=f"{match['job_title']} ({match['match_score']['overall_match']}) \n"
            self.logger.info(f"Fields extracted: {fields}")
            print(fields)
            return fields

        except Exception as e:
            self.logger.error(f"Error processing resume: {e}")
            return {}

    def process_batch(self, input_folder: str, output_file: str):
        """Process multiple resumes in parallel"""
        try:
            pdf_files = list(Path(input_folder).glob("*.pdf"))
            self.logger.info(f"Found {len(pdf_files)} PDF files")
            
            if not pdf_files:
                self.logger.error(f"No PDF files found in {input_folder}")
                return
            
            results = []
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.process_single_resume, str(pdf)) 
                          for pdf in pdf_files]
                
                for future in futures:
                    result = future.result()
                    if result:
                        results.append(result)

            if results:
                self.writer.write_results(results, output_file)
                self.logger.info(f"Results written to {output_file}")
            else:
                self.logger.error("No results to write")

        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")

if __name__ == "__main__":
    analyzer = ResumeAnalyzer()
    
    # # Test single resume processing first
    # test_pdf = r"C:\all\Resume\resume new\captial one\Raghuraj Pratap Yadav.pdf"
    # if os.path.exists(test_pdf):
    #     result = analyzer.process_single_resume(test_pdf)
    #     if result:
    #         analyzer.writer.write_results([result], "single_result.xlsx")
    
    # Process batch if single processing works
    url = r"https://drive.google.com/drive/folders/1inuAWgVsqcw4kmGRy45bx1vJ_WkZHKMG?usp=sharing"
    download_path = download_pdfs_from_folder(url)
    if download_path:
        analyzer.process_batch(download_path, "batch_results.xlsx")