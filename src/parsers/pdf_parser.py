import pymupdf # for PDF parser
import os


class PDFParser:

    def extract_text_from_pdf(self,path):
        """This function takes pdf path and output its text.
        
        Args: 
        path(string): The path to pdf 
        
        Returns:
        String formatted content of PDF"""

        try:
            resume=pymupdf.open(path)
        
            resume_text=[]

            for page_num in range(len(resume)):
                # if resume is of multi page
                page_cont=resume[page_num]
                page_text=page_cont.get_text("text")
                resume_text.append(page_text)
            resume.close()

            return "\n".join(resume_text)
        except Exception as e:
            print(f"Some erroe occur in extracting the text {e}")
            return None
        
    def batch_folder_extraction(self,folder_path):
        """Process multiple PDFs from a folder"""
        results = {}
        for file in os.listdir(folder_path):
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(folder_path, file)
                results[file] = self.extract_text_from_pdf(file_path)
        return results
