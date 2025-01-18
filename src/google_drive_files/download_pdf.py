import gdown
import os
from urllib.parse import urlparse, parse_qs

def download_pdfs_from_folder(folder_url: str) -> str:
    """
    Download all PDFs from Google Drive folder to current directory
    Args:
        folder_url: Google Drive folder shared link
    Returns:
        str: Absolute path where files were downloaded
    """
    try:
        # Get current directory and create downloads folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(current_dir, "downloads")
        os.makedirs(output_dir, exist_ok=True)
        
        # Extract folder ID from URL
        url_parse = urlparse(folder_url)
        if 'folders' in url_parse.path:
            folder_id = url_parse.path.split('/')[-1]
        else:
            query = parse_qs(url_parse.query)
            folder_id = query.get('id', [None])[0]
            
        if not folder_id:
            raise ValueError("Could not extract folder ID from URL")

        # Download folder contents
        url = f"https://drive.google.com/drive/folders/{folder_id}"
        gdown.download_folder(url=url, 
                            output=output_dir,
                            quiet=False)
        
        print(f"Downloads completed to: {output_dir}")
        return output_dir
        
    except Exception as e:
        print(f"Error downloading files: {e}")
        return None

if __name__ == "__main__":
    folder_url = "https://drive.google.com/drive/folders/1inuAWgVsqcw4kmGRy45bx1vJ_WkZHKMG?usp=drive_link"
    download_path = download_pdfs_from_folder(folder_url)
    if download_path:
        print(f"Files downloaded to: {download_path}")