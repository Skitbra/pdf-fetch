#!/usr/bin/env python3
"""
Example usage of Gmail PDF Fetcher
"""
from datetime import datetime, timedelta
from gmail_auth import GmailAuthenticator
from email_search import EmailSearcher
from pdf_downloader import PDFDownloader

def example_basic_usage():
    """Example of basic usage"""
    print("=== Basic Usage Example ===")
    
    # Initialize components
    authenticator = GmailAuthenticator()
    downloader = PDFDownloader()
    
    try:
        # Authenticate
        print("Authenticating with Gmail...")
        service = authenticator.authenticate()
        email_searcher = EmailSearcher(service)
        
        # Set date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Search for emails with PDFs
        query = email_searcher.build_date_query(start_date, end_date, "has:attachment")
        emails = email_searcher.search_emails(query, max_results=10)
        
        print(f"Found {len(emails)} emails")
        
        # Process emails with PDFs
        emails_with_pdfs = []
        for email_msg in emails:
            attachments = email_searcher.get_email_attachments(email_msg)
            if attachments:
                metadata = email_searcher.get_email_metadata(email_msg)
                emails_with_pdfs.append({
                    'message': email_msg,
                    'attachments': attachments,
                    'metadata': metadata
                })
        
        print(f"Found {len(emails_with_pdfs)} emails with PDF attachments")
        
        # Download PDFs
        if emails_with_pdfs:
            downloaded_files = downloader.download_pdfs_from_emails(
                emails_with_pdfs, email_searcher
            )
            
            summary = downloader.get_download_summary(downloaded_files)
            print(f"Downloaded {summary['total_files']} PDFs")
            print(f"Total size: {summary['total_size_mb']} MB")
        
    except Exception as e:
        print(f"Error: {e}")

def example_advanced_search():
    """Example of advanced search with specific criteria"""
    print("\n=== Advanced Search Example ===")
    
    authenticator = GmailAuthenticator()
    
    try:
        service = authenticator.authenticate()
        email_searcher = EmailSearcher(service)
        
        # Search for emails from specific sender in last week
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Custom search query
        base_query = "from:bank@example.com subject:statement"
        query = email_searcher.build_date_query(start_date, end_date, base_query)
        
        print(f"Search query: {query}")
        
        emails = email_searcher.search_emails(query, max_results=5)
        print(f"Found {len(emails)} emails matching criteria")
        
        # Show email details
        for email_msg in emails:
            metadata = email_searcher.get_email_metadata(email_msg)
            attachments = email_searcher.get_email_attachments(email_msg)
            
            print(f"\nEmail: {metadata.get('subject', 'No subject')}")
            print(f"From: {metadata.get('from', 'Unknown')}")
            print(f"Date: {metadata.get('date', 'Unknown')}")
            print(f"PDF attachments: {len(attachments)}")
            
            for attachment in attachments:
                print(f"  - {attachment['filename']} ({attachment['size']} bytes)")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Gmail PDF Fetcher - Example Usage")
    print("=" * 40)
    
    # Run examples
    example_basic_usage()
    example_advanced_search()
    
    print("\n" + "=" * 40)
    print("Examples completed!")
    print("\nTo run the full program, use:")
    print("python main.py --start-date 2024-01-01 --end-date 2024-01-31")

