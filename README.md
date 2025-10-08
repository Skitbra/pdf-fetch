# Gmail PDF Fetcher

A Python program to automatically download PDF attachments from Gmail emails within a specified date range, with full support for 2FA authentication.

## Features

- 🔐 **2FA Support**: Full OAuth2 authentication with 2FA support
- 📅 **Date Range Filtering**: Download PDFs from emails within specific date ranges
- 🔍 **Advanced Search**: Use Gmail search syntax for precise email filtering
- 📁 **Smart File Management**: Automatic filename sanitization and conflict resolution
- 📊 **Download Summary**: Detailed reports of downloaded files
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🖥️ **CLI Interface**: Easy-to-use command-line interface

## Prerequisites

- Python 3.7 or higher
- Gmail account with 2FA enabled (recommended)
- Google Cloud Project with Gmail API enabled

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd pdf-fetch
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Go to "Credentials" and create OAuth 2.0 Client ID
   - Download the credentials JSON file

5. **Configure environment (optional):**
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"
   export DOWNLOAD_DIR="/path/to/download/directory"
   export EMAIL_QUERY="has:attachment"
   ```

### Virtual Environment Notes

- **Always activate the virtual environment** before running the program:
  ```bash
  source venv/bin/activate  # macOS/Linux
  # or
  venv\Scripts\activate     # Windows
  ```

- **Deactivate when done:**
  ```bash
  deactivate
  ```

- **The virtual environment** keeps dependencies isolated from your system Python installation
- **Never commit** the `venv/` folder to version control (it's already in `.gitignore`)

## Usage

### Basic Usage

**Make sure your virtual environment is activated first:**
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows
```

Download all PDFs from emails between two dates:

```bash
python main.py --start-date 2024-01-01 --end-date 2024-01-31
```

### Advanced Usage

```bash
# Download PDFs from specific sender
python main.py -s 2024-01-01 -e 2024-01-31 -q "from:bank@example.com"

# Specify custom download directory
python main.py -s 2024-01-01 -e 2024-01-31 -d ./bank_statements

# Use custom credentials file
python main.py -s 2024-01-01 -e 2024-01-31 -c ./my_credentials.json

# Limit number of emails processed
python main.py -s 2024-01-01 -e 2024-01-31 -m 50

# Enable verbose logging
python main.py -s 2024-01-01 -e 2024-01-31 -v
```

### Command Line Options

- `-s, --start-date`: Start date in YYYY-MM-DD format (required)
- `-e, --end-date`: End date in YYYY-MM-DD format (required)
- `-q, --query`: Additional Gmail search query (optional)
- `-m, --max-results`: Maximum number of emails to process (default: 100)
- `-d, --download-dir`: Directory to save downloaded PDFs (default: ./downloads)
- `-c, --credentials`: Path to Google OAuth2 credentials JSON file
- `-v, --verbose`: Enable verbose logging

### Gmail Search Query Examples

You can use Gmail's powerful search syntax with the `-q` option:

```bash
# From specific sender
python main.py -s 2024-01-01 -e 2024-01-31 -q "from:example@gmail.com"

# Subject contains specific text
python main.py -s 2024-01-01 -e 2024-01-31 -q "subject:invoice"

# Multiple conditions
python main.py -s 2024-01-01 -e 2024-01-31 -q "from:bank@example.com subject:statement"

# Has attachments (default behavior)
python main.py -s 2024-01-01 -e 2024-01-31 -q "has:attachment"
```

## Authentication Process

1. **First Run**: When you run the program for the first time, it will:
   - Open your web browser
   - Ask you to sign in to your Google account
   - Request permission to access your Gmail
   - Save the authentication token for future use

2. **Subsequent Runs**: The program will use the saved token automatically

3. **Token Refresh**: If the token expires, the program will automatically refresh it

## File Organization

Downloaded PDFs are organized with descriptive filenames:

```
downloads/
├── 20240115_143022_bank_statement.pdf
├── 20240116_091545_company_invoice.pdf
└── 20240117_162330_utility_bill.pdf
```

Filename format: `YYYYMMDD_HHMMSS_sender_filename.pdf`

## Configuration

### Environment Variables

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google OAuth2 credentials JSON file
- `DOWNLOAD_DIR`: Default download directory (default: ./downloads)
- `EMAIL_QUERY`: Default email search query (default: has:attachment)

### Configuration File

Create a `.env` file in the project root:

```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
DOWNLOAD_DIR=./downloads
EMAIL_QUERY=has:attachment
```

## Logging

The program creates detailed logs in `pdf_fetcher.log` and displays progress in the console. Use the `-v` flag for verbose output.

## Error Handling

The program includes comprehensive error handling for:
- Authentication failures
- Network connectivity issues
- Invalid date formats
- File system errors
- Gmail API rate limits

## Security

- All authentication is handled through Google's OAuth2 system
- Credentials are stored locally and encrypted
- The program only requests read-only access to Gmail
- No email content is stored, only PDF attachments

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure your credentials file is correct and the Gmail API is enabled
2. **No PDFs Found**: Check your date range and search query
3. **Permission Denied**: Ensure you have write permissions to the download directory
4. **Rate Limit Exceeded**: The Gmail API has rate limits; try reducing the date range or max results

### Getting Help

Check the log file `pdf_fetcher.log` for detailed error information.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.