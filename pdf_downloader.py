"""
PDF download and management functionality
"""
import os
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

from config import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

class PDFDownloader:
    def __init__(self, download_dir: str = None):
        """
        Initialize PDF downloader
        
        Args:
            download_dir (str): Directory to save downloaded PDFs
        """
        self.download_dir = Path(download_dir or DOWNLOAD_DIR)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for safe file system usage
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Ensure it's not empty
        if not filename:
            filename = 'unnamed_pdf'
        
        # Ensure it has .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'
        
        return filename
    
    def generate_unique_filename(self, base_filename: str, email_metadata: Dict) -> str:
        """
        Generate unique filename to avoid conflicts
        
        Args:
            base_filename (str): Base filename
            email_metadata (Dict): Email metadata for context
            
        Returns:
            str: Unique filename
        """
        # Sanitize the base filename
        safe_filename = self.sanitize_filename(base_filename)
        
        # Extract date from email metadata
        email_date = email_metadata.get('date', '')
        if email_date:
            try:
                # Parse email date and format it
                from email.utils import parsedate_to_datetime
                parsed_date = parsedate_to_datetime(email_date)
                date_str = parsed_date.strftime('%Y%m%d_%H%M%S')
            except:
                date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        else:
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract sender info for context
        sender = email_metadata.get('from', 'unknown')
        sender_clean = re.sub(r'[<>:"/\\|?*]', '_', sender.split('@')[0] if '@' in sender else sender)
        
        # Create filename with context
        name_parts = safe_filename.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            unique_filename = f"{date_str}_{sender_clean}_{name}.{ext}"
        else:
            unique_filename = f"{date_str}_{sender_clean}_{safe_filename}"
        
        # Check if file exists and add counter if needed
        counter = 1
        original_filename = unique_filename
        while (self.download_dir / unique_filename).exists():
            name_parts = original_filename.rsplit('.', 1)
            if len(name_parts) == 2:
                name, ext = name_parts
                unique_filename = f"{name}_{counter}.{ext}"
            else:
                unique_filename = f"{original_filename}_{counter}"
            counter += 1
        
        return unique_filename
    
    def download_pdf(self, attachment_data: bytes, filename: str, email_metadata: Dict) -> Optional[str]:
        """
        Download PDF attachment to local directory
        
        Args:
            attachment_data (bytes): PDF file data
            filename (str): Original filename
            email_metadata (Dict): Email metadata
            
        Returns:
            Optional[str]: Path to downloaded file if successful, None otherwise
        """
        try:
            # Generate unique filename
            unique_filename = self.generate_unique_filename(filename, email_metadata)
            file_path = self.download_dir / unique_filename
            
            # Write file data
            with open(file_path, 'wb') as f:
                f.write(attachment_data)
            
            logger.info(f"Downloaded PDF: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Error downloading PDF {filename}: {e}")
            return None
    
    def download_pdfs_from_emails(self, emails_with_pdfs: List[Dict], email_searcher) -> List[str]:
        """
        Download all PDFs from a list of emails
        
        Args:
            emails_with_pdfs (List[Dict]): List of emails containing PDFs
            email_searcher: EmailSearcher instance for downloading attachments
            
        Returns:
            List[str]: List of downloaded file paths
        """
        downloaded_files = []
        
        for email_data in emails_with_pdfs:
            message = email_data['message']
            attachments = email_data['attachments']
            metadata = email_data['metadata']
            
            logger.info(f"Processing email: {metadata.get('subject', 'No subject')}")
            
            for attachment in attachments:
                try:
                    # Download attachment data
                    attachment_data = email_searcher.get_attachment_data(
                        message['id'], 
                        attachment['attachment_id']
                    )
                    
                    if attachment_data:
                        # Download PDF
                        file_path = self.download_pdf(
                            attachment_data, 
                            attachment['filename'], 
                            metadata
                        )
                        
                        if file_path:
                            downloaded_files.append(file_path)
                    else:
                        logger.warning(f"Failed to download attachment: {attachment['filename']}")
                        
                except Exception as e:
                    logger.error(f"Error processing attachment {attachment['filename']}: {e}")
                    continue
        
        return downloaded_files
    
    def get_download_summary(self, downloaded_files: List[str]) -> Dict:
        """
        Generate summary of downloaded files
        
        Args:
            downloaded_files (List[str]): List of downloaded file paths
            
        Returns:
            Dict: Download summary
        """
        total_size = 0
        file_info = []
        
        for file_path in downloaded_files:
            try:
                file_stat = Path(file_path).stat()
                size = file_stat.st_size
                total_size += size
                
                file_info.append({
                    'path': file_path,
                    'size': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                })
            except Exception as e:
                logger.error(f"Error getting file info for {file_path}: {e}")
        
        return {
            'total_files': len(downloaded_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'files': file_info
        }

