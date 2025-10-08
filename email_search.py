"""
Email search functionality with date range filtering
"""
import base64
import email
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class EmailSearcher:
    def __init__(self, gmail_service):
        """
        Initialize email searcher
        
        Args:
            gmail_service: Gmail API service object
        """
        self.service = gmail_service
        
    def build_date_query(self, start_date: datetime, end_date: datetime, base_query: str = "") -> str:
        """
        Build Gmail search query with date range
        
        Args:
            start_date (datetime): Start date for search
            end_date (datetime): End date for search
            base_query (str): Additional search criteria
            
        Returns:
            str: Complete Gmail search query
        """
        # Format dates for Gmail search (YYYY/MM/DD)
        start_str = start_date.strftime('%Y/%m/%d')
        end_str = end_date.strftime('%Y/%m/%d')
        
        # Build date range query
        date_query = f"after:{start_str} before:{end_str}"
        
        # Combine with base query
        if base_query:
            return f"{base_query} {date_query}"
        return date_query
    
    def search_emails(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search for emails using Gmail API
        
        Args:
            query (str): Gmail search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict]: List of email message objects
        """
        try:
            logger.info(f"Searching emails with query: {query}")
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} emails")
            
            # Get full message details
            email_details = []
            for message in messages:
                try:
                    msg = self.service.users().messages().get(
                        userId='me', 
                        id=message['id']
                    ).execute()
                    email_details.append(msg)
                except Exception as e:
                    logger.error(f"Error fetching message {message['id']}: {e}")
                    continue
            
            return email_details
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
    
    def get_email_attachments(self, message: Dict) -> List[Dict]:
        """
        Extract attachment information from email message
        
        Args:
            message (Dict): Email message object from Gmail API
            
        Returns:
            List[Dict]: List of attachment information
        """
        attachments = []
        
        try:
            payload = message.get('payload', {})
            
            # Handle multipart messages
            if 'parts' in payload:
                for part in payload['parts']:
                    attachments.extend(self._extract_attachments_from_part(part))
            else:
                # Single part message
                attachments.extend(self._extract_attachments_from_part(payload))
                
        except Exception as e:
            logger.error(f"Error extracting attachments: {e}")
            
        return attachments
    
    def _extract_attachments_from_part(self, part: Dict) -> List[Dict]:
        """
        Extract attachments from a message part
        
        Args:
            part (Dict): Message part object
            
        Returns:
            List[Dict]: List of attachment information
        """
        attachments = []
        
        # Check if this part has attachments
        if part.get('filename'):
            filename = part['filename']
            mime_type = part.get('mimeType', '')
            
            # Check if it's a PDF
            if mime_type == 'application/pdf' or filename.lower().endswith('.pdf'):
                attachment_info = {
                    'filename': filename,
                    'mime_type': mime_type,
                    'part_id': part.get('partId'),
                    'size': part.get('body', {}).get('size', 0),
                    'attachment_id': part.get('body', {}).get('attachmentId')
                }
                attachments.append(attachment_info)
                logger.info(f"Found PDF attachment: {filename}")
        
        # Recursively check nested parts
        if 'parts' in part:
            for subpart in part['parts']:
                attachments.extend(self._extract_attachments_from_part(subpart))
        
        return attachments
    
    def get_attachment_data(self, message_id: str, attachment_id: str) -> bytes:
        """
        Download attachment data from Gmail
        
        Args:
            message_id (str): Gmail message ID
            attachment_id (str): Gmail attachment ID
            
        Returns:
            bytes: Attachment data
        """
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me',
                messageId=message_id,
                id=attachment_id
            ).execute()
            
            # Decode base64 data
            data = attachment['data']
            return base64.urlsafe_b64decode(data)
            
        except Exception as e:
            logger.error(f"Error downloading attachment {attachment_id}: {e}")
            return b''
    
    def get_email_metadata(self, message: Dict) -> Dict:
        """
        Extract metadata from email message
        
        Args:
            message (Dict): Email message object
            
        Returns:
            Dict: Email metadata
        """
        headers = message.get('payload', {}).get('headers', [])
        metadata = {}
        
        for header in headers:
            name = header['name'].lower()
            value = header['value']
            
            if name == 'from':
                metadata['from'] = value
            elif name == 'to':
                metadata['to'] = value
            elif name == 'subject':
                metadata['subject'] = value
            elif name == 'date':
                metadata['date'] = value
        
        metadata['message_id'] = message['id']
        metadata['thread_id'] = message['threadId']
        
        return metadata

