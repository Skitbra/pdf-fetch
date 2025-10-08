#!/usr/bin/env python3
"""
Gmail PDF Fetcher - Main program
Downloads PDF attachments from Gmail emails within a date range
"""
import click
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import sys

from gmail_auth import GmailAuthenticator
from email_search import EmailSearcher
from pdf_downloader import PDFDownloader
from config import EMAIL_QUERY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_fetcher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class GmailPDFFetcher:
    def __init__(self, credentials_file: str = None, download_dir: str = None):
        """
        Initialize Gmail PDF Fetcher
        
        Args:
            credentials_file (str): Path to Google OAuth2 credentials JSON file
            download_dir (str): Directory to save downloaded PDFs
        """
        self.authenticator = GmailAuthenticator(credentials_file)
        self.downloader = PDFDownloader(download_dir)
        self.email_searcher = None
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            service = self.authenticator.authenticate()
            self.email_searcher = EmailSearcher(service)
            logger.info("Authentication successful")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def fetch_pdfs(self, start_date: datetime, end_date: datetime, 
                   query: str = None, max_results: int = 100) -> List[str]:
        """
        Fetch PDFs from Gmail within date range
        
        Args:
            start_date (datetime): Start date for search
            end_date (datetime): End date for search
            query (str): Additional search criteria
            max_results (int): Maximum number of emails to process
            
        Returns:
            List[str]: List of downloaded file paths
        """
        if not self.email_searcher:
            logger.error("Not authenticated. Please authenticate first.")
            return []
        
        try:
            # Build search query
            base_query = query or EMAIL_QUERY
            search_query = self.email_searcher.build_date_query(start_date, end_date, base_query)
            
            logger.info(f"Searching for emails from {start_date.date()} to {end_date.date()}")
            logger.info(f"Search query: {search_query}")
            
            # Search for emails
            emails = self.email_searcher.search_emails(search_query, max_results)
            
            if not emails:
                logger.info("No emails found matching criteria")
                return []
            
            # Find emails with PDF attachments
            emails_with_pdfs = []
            for email_msg in emails:
                attachments = self.email_searcher.get_email_attachments(email_msg)
                if attachments:
                    metadata = self.email_searcher.get_email_metadata(email_msg)
                    emails_with_pdfs.append({
                        'message': email_msg,
                        'attachments': attachments,
                        'metadata': metadata
                    })
            
            logger.info(f"Found {len(emails_with_pdfs)} emails with PDF attachments")
            
            if not emails_with_pdfs:
                logger.info("No PDF attachments found in emails")
                return []
            
            # Download PDFs
            downloaded_files = self.downloader.download_pdfs_from_emails(
                emails_with_pdfs, self.email_searcher
            )
            
            return downloaded_files
            
        except Exception as e:
            logger.error(f"Error fetching PDFs: {e}")
            return []

@click.command()
@click.option('--start-date', '-s', required=True, 
              help='Start date (YYYY-MM-DD format)')
@click.option('--end-date', '-e', required=True,
              help='End date (YYYY-MM-DD format)')
@click.option('--query', '-q', default=None,
              help='Additional Gmail search query (e.g., "from:example@gmail.com")')
@click.option('--max-results', '-m', default=100,
              help='Maximum number of emails to process')
@click.option('--download-dir', '-d', default=None,
              help='Directory to save downloaded PDFs')
@click.option('--credentials', '-c', default=None,
              help='Path to Google OAuth2 credentials JSON file')
@click.option('--verbose', '-v', is_flag=True,
              help='Enable verbose logging')
def main(start_date, end_date, query, max_results, download_dir, credentials, verbose):
    """
    Gmail PDF Fetcher
    
    Downloads PDF attachments from Gmail emails within a specified date range.
    Supports 2FA authentication through Google OAuth2.
    
    Example usage:
    python main.py --start-date 2024-01-01 --end-date 2024-01-31
    python main.py -s 2024-01-01 -e 2024-01-31 -q "from:bank@example.com" -d ./bank_statements
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Parse dates
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start_dt >= end_dt:
            click.echo("Error: Start date must be before end date", err=True)
            sys.exit(1)
        
        # Initialize fetcher
        fetcher = GmailPDFFetcher(credentials, download_dir)
        
        # Authenticate
        click.echo("Authenticating with Gmail...")
        if not fetcher.authenticate():
            click.echo("Authentication failed. Please check your credentials.", err=True)
            sys.exit(1)
        
        click.echo("Authentication successful!")
        
        # Fetch PDFs
        click.echo(f"Fetching PDFs from {start_date} to {end_date}...")
        downloaded_files = fetcher.fetch_pdfs(start_dt, end_dt, query, max_results)
        
        if downloaded_files:
            # Generate summary
            summary = fetcher.downloader.get_download_summary(downloaded_files)
            
            click.echo(f"\n✅ Successfully downloaded {summary['total_files']} PDF files")
            click.echo(f"📁 Total size: {summary['total_size_mb']} MB")
            click.echo(f"📂 Saved to: {fetcher.downloader.download_dir}")
            
            if verbose:
                click.echo("\nDownloaded files:")
                for file_info in summary['files']:
                    click.echo(f"  - {file_info['path']} ({file_info['size_mb']} MB)")
        else:
            click.echo("No PDFs were downloaded.")
        
    except ValueError as e:
        click.echo(f"Error: Invalid date format. Use YYYY-MM-DD format. {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
