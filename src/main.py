import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from parsers.pdf_parser import PDFParser
from extractors.field_extractor import FieldExtractor
from google_drive_files.download_pdf import download_pdfs_from_folder
# from extractors.score_calculator import ScoreCalculator
from utils.excel_writer import ExcelWriter

class ResumeAnalyzer:
    def __init__(self):
        self.parser = PDFParser()
        self.extractor = FieldExtractor()
        # self.scorer = ScoreCalculator()
        self.writer = ExcelWriter()
    def process_single_resume(self, pdf_path: str):
        """Process a single resume"""
        text = self.parser.extract_text_from_pdf(pdf_path)
        # print(text)
        if not text:
            return {}
            
        fields = self.extractor.extract_fields(text)
        print(fields)
        print(fields["course"])
        # scores = self.scorer.calculate_scores(fields)
        # fields.update(scores)
        return fields

    def process_batch(self, input_folder: str, output_file: str):
        """Process multiple resumes in parallel"""
        pdf_files = [f for f in Path(input_folder).glob("*.pdf")]
        
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(self.process_single_resume, str(pdf)) 
                      for pdf in pdf_files]
            
            for future in futures:
                result = future.result()
                if result:
                    results.append(result)

        self.writer.write_results(results, output_file)
        # self.writer.create_summary_sheet(output_file)

if __name__ == "__main__":
    analyzer = ResumeAnalyzer()
    url=r"https://drive.google.com/drive/folders/1inuAWgVsqcw4kmGRy45bx1vJ_WkZHKMG?usp=sharing"
    download_pdfs_from_folder(url)
    analyzer.process_batch(os.path.join(os.getcwd(),"google_drive_files/downloads"), "results.xlsx")
    # analyzer.process_single_resume(r"C:\all\Resume\resume new\captial one\Raghuraj Pratap Yadav.pdf")


# Stilll need to be corrected