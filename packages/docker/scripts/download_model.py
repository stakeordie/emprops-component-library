#!/usr/bin/env python3
import os
import sys
import logging
from typing import Optional
from urllib.parse import urlparse
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/tmp/model_download.log')
    ]
)
logger = logging.getLogger(__name__)

def try_huggingface_download(url: str, output_path: str, filename: str) -> bool:
    """
    Attempt to download using Hugging Face Hub API.
    Returns True if successful, False otherwise.
    """
    try:
        from huggingface_hub import hf_hub_download
        from huggingface_hub.utils import enable_progress_bars

        enable_progress_bars()
        
        # Parse HF URL to get repo_id and filename
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        
        if len(path_parts) < 4:  # Need at least org/repo/resolve/filename
            return False
            
        repo_id = f"{path_parts[0]}/{path_parts[1]}"
        revision = path_parts[3] if path_parts[2] in ['resolve', 'raw'] else None
        hf_filename = path_parts[-1]
        
        logger.info(f"Attempting HF download: repo={repo_id}, file={hf_filename}, rev={revision}")
        
        # Download using hf_hub_download
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=hf_filename,
            revision=revision,
            local_dir=output_path
        )
        
        # Move to final location if needed
        final_path = os.path.join(output_path, filename)
        if downloaded_path != final_path:
            os.rename(downloaded_path, final_path)
            
        return os.path.exists(final_path)
        
    except Exception as e:
        logger.error(f"HF download failed: {str(e)}")
        return False

def download_with_wget(url: str, output_path: str, filename: str) -> bool:
    """
    Download file using wget.
    Returns True if successful, False otherwise.
    """
    try:
        output_file = os.path.join(output_path, filename)
        command = ['wget', '--progress=bar:force:noscroll', '-O', output_file, url]
        
        logger.info(f"Downloading with wget: {url}")
        result = subprocess.run(command, capture_output=True, text=True)
        
        return result.returncode == 0 and os.path.exists(output_file)
        
    except Exception as e:
        logger.error(f"wget download failed: {str(e)}")
        return False

def main():
    if len(sys.argv) != 4:
        logger.error("Usage: download_model.py <url> <output_path> <filename>")
        return 1
        
    url = sys.argv[1]
    output_path = sys.argv[2]
    filename = sys.argv[3]
    
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)
    
    # Try Hugging Face download first if it's a HF URL
    if 'huggingface.co' in url:
        if try_huggingface_download(url, output_path, filename):
            logger.info("Successfully downloaded using Hugging Face")
            return 0
        logger.warning("Hugging Face download failed, falling back to wget")
    
    # Fall back to wget
    if download_with_wget(url, output_path, filename):
        logger.info("Successfully downloaded using wget")
        return 0
    
    logger.error("All download attempts failed")
    return 1

if __name__ == "__main__":
    sys.exit(main())
