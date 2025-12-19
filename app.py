#!/usr/bin/env python3
"""
Flask Web API for Gmail PDF Fetcher
Provides a web interface for downloading PDF attachments from Gmail
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import threading
import time

from main import GmailPDFFetcher
from config import DOWNLOAD_DIR

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variables to track job status
job_status = {}
job_results = {}

class PDFFetchJob:
    def __init__(self, job_id: str, start_date: str, end_date: str, 
                 query: str = None, download_dir: str = None, max_results: int = 100):
        self.job_id = job_id
        self.start_date = start_date
        self.end_date = end_date
        self.query = query
        self.download_dir = download_dir or DOWNLOAD_DIR
        self.max_results = max_results
        self.status = "pending"
        self.progress = 0
        self.message = "Initializing..."
        self.downloaded_files = []
        self.error = None
        
    def run(self):
        """Execute the PDF fetch job"""
        try:
            job_status[self.job_id] = self
            self.status = "running"
            self.message = "Authenticating with Gmail..."
            
            # Parse dates
            start_dt = datetime.strptime(self.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(self.end_date, '%Y-%m-%d')
            
            # Initialize fetcher
            fetcher = GmailPDFFetcher(download_dir=self.download_dir)
            
            # Authenticate
            self.progress = 10
            if not fetcher.authenticate():
                raise Exception("Authentication failed")
            
            self.progress = 20
            self.message = "Searching for emails..."
            
            # Fetch PDFs
            self.downloaded_files = fetcher.fetch_pdfs(
                start_dt, end_dt, self.query, self.max_results
            )
            
            self.progress = 100
            self.status = "completed"
            self.message = f"Successfully downloaded {len(self.downloaded_files)} PDF files"
            
            # Store results
            if self.downloaded_files:
                summary = fetcher.downloader.get_download_summary(self.downloaded_files)
                job_results[self.job_id] = {
                    'files': self.downloaded_files,
                    'summary': summary,
                    'download_dir': str(fetcher.downloader.download_dir)
                }
            else:
                job_results[self.job_id] = {
                    'files': [],
                    'summary': {'total_files': 0, 'total_size_mb': 0},
                    'download_dir': str(fetcher.downloader.download_dir)
                }
                
        except Exception as e:
            self.status = "failed"
            self.error = str(e)
            self.message = f"Error: {e}"
            logger.error(f"Job {self.job_id} failed: {e}")

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/api/fetch', methods=['POST'])
def start_fetch():
    """Start a new PDF fetch job"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('start_date') or not data.get('end_date'):
            return jsonify({'error': 'Start date and end date are required'}), 400
        
        # Generate job ID
        job_id = f"job_{int(time.time())}"
        
        # Create and start job
        job = PDFFetchJob(
            job_id=job_id,
            start_date=data['start_date'],
            end_date=data['end_date'],
            query=data.get('query'),
            download_dir=data.get('download_dir'),
            max_results=data.get('max_results', 100)
        )
        
        # Start job in background thread
        thread = threading.Thread(target=job.run)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'PDF fetch job started'
        })
        
    except Exception as e:
        logger.error(f"Error starting fetch job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<job_id>')
def get_job_status(job_id):
    """Get the status of a PDF fetch job"""
    try:
        if job_id not in job_status:
            return jsonify({'error': 'Job not found'}), 404
        
        job = job_status[job_id]
        
        response = {
            'job_id': job_id,
            'status': job.status,
            'progress': job.progress,
            'message': job.message
        }
        
        if job.error:
            response['error'] = job.error
            
        if job.status == 'completed' and job_id in job_results:
            response['results'] = job_results[job_id]
            
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<job_id>')
def get_job_results(job_id):
    """Get the results of a completed PDF fetch job"""
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Results not found'}), 404
        
        return jsonify(job_results[job_id])
        
    except Exception as e:
        logger.error(f"Error getting job results: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<job_id>/<filename>')
def download_file(job_id, filename):
    """Download a specific PDF file from job results"""
    try:
        if job_id not in job_results:
            return jsonify({'error': 'Job results not found'}), 404
        
        results = job_results[job_id]
        download_dir = results['download_dir']
        
        # Find the file in the results
        file_path = None
        for file in results['files']:
            if Path(file).name == filename:
                file_path = file
                break
        
        if not file_path or not Path(file_path).exists():
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directories')
def get_directories():
    """Get list of available directories for download"""
    try:
        # Get common directories
        home_dir = Path.home()
        directories = [
            {'path': str(home_dir / 'Downloads'), 'name': 'Downloads', 'type': 'system'},
            {'path': str(home_dir / 'Documents'), 'name': 'Documents', 'type': 'system'},
            {'path': str(home_dir / 'Desktop'), 'name': 'Desktop', 'type': 'system'},
            {'path': str(Path.cwd() / 'pdfs'), 'name': 'Project PDFs', 'type': 'project'},
            {'path': str(Path.cwd() / 'downloads'), 'name': 'Project Downloads', 'type': 'project'},
        ]
        
        # Add all directories and mark which exist
        result_dirs = []
        for dir_info in directories:
            dir_path = Path(dir_info['path'])
            dir_info['exists'] = dir_path.exists()
            dir_info['writable'] = dir_path.exists() and os.access(dir_path, os.W_OK)
            result_dirs.append(dir_info)
        
        return jsonify(result_dirs)
        
    except Exception as e:
        logger.error(f"Error getting directories: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directories/contents')
def get_directory_contents():
    """Get contents of a specific directory"""
    try:
        dir_path = request.args.get('path')
        if not dir_path:
            return jsonify({'error': 'Directory path is required'}), 400
        
        path = Path(dir_path)
        if not path.exists():
            return jsonify({'error': 'Directory does not exist'}), 404
        
        if not path.is_dir():
            return jsonify({'error': 'Path is not a directory'}), 400
        
        contents = []
        try:
            for item in path.iterdir():
                if item.name.startswith('.'):  # Skip hidden files
                    continue
                    
                item_info = {
                    'name': item.name,
                    'path': str(item),
                    'is_dir': item.is_dir(),
                    'size': 0,
                    'modified': ''
                }
                
                try:
                    stat = item.stat()
                    if not item.is_dir():
                        item_info['size'] = stat.st_size
                        item_info['size_mb'] = round(stat.st_size / (1024 * 1024), 2)
                    item_info['modified'] = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                except (OSError, PermissionError):
                    pass
                
                contents.append(item_info)
        except PermissionError:
            return jsonify({'error': 'Permission denied accessing directory'}), 403
        
        # Sort: directories first, then files, both alphabetically
        contents.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return jsonify({
            'path': str(path),
            'contents': contents,
            'total_items': len(contents)
        })
        
    except Exception as e:
        logger.error(f"Error getting directory contents: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directories/create', methods=['POST'])
def create_directory():
    """Create a new directory"""
    try:
        data = request.get_json()
        dir_path = data.get('path')
        
        if not dir_path:
            return jsonify({'error': 'Directory path is required'}), 400
        
        path = Path(dir_path)
        
        # Check if parent directory exists and is writable
        parent = path.parent
        if not parent.exists():
            return jsonify({'error': 'Parent directory does not exist'}), 400
        
        if not os.access(parent, os.W_OK):
            return jsonify({'error': 'No write permission to parent directory'}), 403
        
        # Check if directory already exists
        if path.exists():
            if path.is_dir():
                return jsonify({'message': 'Directory already exists', 'path': str(path)})
            else:
                return jsonify({'error': 'A file with this name already exists'}), 400
        
        # Create the directory
        path.mkdir(parents=True, exist_ok=True)
        
        return jsonify({
            'message': 'Directory created successfully',
            'path': str(path),
            'name': path.name
        })
        
    except PermissionError:
        return jsonify({'error': 'Permission denied creating directory'}), 403
    except Exception as e:
        logger.error(f"Error creating directory: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directories/validate', methods=['POST'])
def validate_directory():
    """Validate if a directory path is valid and writable"""
    try:
        data = request.get_json()
        dir_path = data.get('path')
        
        if not dir_path:
            return jsonify({'error': 'Directory path is required'}), 400
        
        path = Path(dir_path)
        
        result = {
            'path': str(path),
            'exists': path.exists(),
            'is_dir': path.is_dir() if path.exists() else None,
            'writable': False,
            'parent_exists': path.parent.exists(),
            'parent_writable': False,
            'valid': False
        }
        
        if path.exists():
            if path.is_dir():
                result['writable'] = os.access(path, os.W_OK)
                result['valid'] = result['writable']
            else:
                result['error'] = 'Path exists but is not a directory'
        else:
            # Check if we can create it
            if path.parent.exists():
                result['parent_writable'] = os.access(path.parent, os.W_OK)
                result['valid'] = result['parent_writable']
            else:
                result['error'] = 'Parent directory does not exist'
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error validating directory: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    Path('templates').mkdir(exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
