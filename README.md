# Gmail PDF Fetcher

A Python program to automatically download PDF attachments from Gmail emails within a specified date range, with full support for 2FA authentication. Now includes a modern web interface!

## Features

- 🔐 **2FA Support**: Full OAuth2 authentication with 2FA support
- 📅 **Date Range Filtering**: Download PDFs from emails within specific date ranges
- 🔍 **Advanced Search**: Use Gmail search syntax for precise email filtering
- 📁 **Smart File Management**: Automatic filename sanitization and conflict resolution
- 📊 **Download Summary**: Detailed reports of downloaded files
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 🌐 **Web Interface**: Modern, responsive web UI for easy interaction

## Prerequisites

- Python 3.7 or higher
- Gmail account with 2FA enabled (recommended)
- Google Cloud Project with Gmail API enabled
- PyCharm (Community or Professional Edition)

## Installation

1. **Clone the repository in PyCharm:**
   - `VCS` → `Get from Version Control`
   - Enter the repository URL
   - Choose a local directory
   - Click `Clone`

2. **Set up virtual environment:**
   - PyCharm will detect `requirements.txt` and offer to install dependencies
   - Or manually configure:
     - Go to `File` → `Settings` → `Project` → `Python Interpreter`
     - Click the gear icon ⚙️ → `Add`
     - Select `Virtualenv Environment` → `New environment`
     - Set location to `venv` in your project directory
     - Click `OK`
   - PyCharm will automatically activate the virtual environment for all terminals and runs

3. **Install dependencies:**
   - Open `requirements.txt` in PyCharm
   - Click the banner at the top to install all packages
   - Or use PyCharm's built-in terminal (venv is auto-activated):
     ```bash
     pip install -r requirements.txt
     ```

4. **Set up Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Go to "Credentials" and create OAuth 2.0 Client ID
   - Download the credentials JSON file to your project directory

5. **Configure environment variables (optional):**
   - Go to `Run` → `Edit Configurations`
   - Select your run configuration (or create one)
   - Add environment variables in the `Environment variables` field
   - Format: `KEY=value;KEY2=value2` (use `;` as separator)
   - Example variables:
     - `GOOGLE_APPLICATION_CREDENTIALS=./credentials.json`
     - `DOWNLOAD_DIR=./downloads`
     - `EMAIL_QUERY=has:attachment`

## PyCharm Setup Notes

- **Virtual Environment**: PyCharm automatically manages the virtual environment
  - Look for "(venv)" in the terminal prompt to confirm activation
  - The virtual environment keeps dependencies isolated from your system Python
  - Never commit the `venv/` folder to version control (it's in `.gitignore`)

- **Run Configurations**: Create run configurations for easy execution
  - Right-click `run_web.py` or `main.py` → `Run`
  - PyCharm creates a run configuration automatically
  - Edit via `Run` → `Edit Configurations`

- **Terminal**: PyCharm's built-in terminal automatically uses the project's virtual environment

## Usage

### Web Interface (Recommended)

1. Right-click on `run_web.py` in the Project explorer
2. Select `Run 'run_web'`
3. Or press `Ctrl+Shift+F10` (Windows/Linux) or `⌃⇧R` (macOS)
4. The Run panel will open at the bottom showing server status
5. Click the URL (http://localhost:5000) in the console to open the browser

This will:
- Start a local web server at http://localhost:5000
- Automatically open your web browser
- Provide an intuitive interface for:
  - Selecting date ranges with a calendar picker
  - Entering Gmail search queries
  - Choosing download directories
  - Monitoring download progress in real-time
  - Viewing and downloading results

### Command Line Interface (via PyCharm)

**Basic Usage:**

1. Right-click on `main.py` → `More Run/Debug` → `Modify Run Configuration`
2. In the `Parameters` field, add:
   ```
   --start-date 2024-01-01 --end-date 2024-01-31
   ```
3. Click `OK` and run the configuration

**Advanced Usage - Configure Parameters:**

In the Run Configuration's `Parameters` field, you can add:

```
# Download PDFs from specific sender
-s 2024-01-01 -e 2024-01-31 -q "from:bank@example.com"

# Specify custom download directory
-s 2024-01-01 -e 2024-01-31 -d ./bank_statements

# Use custom credentials file
-s 2024-01-01 -e 2024-01-31 -c ./my_credentials.json

# Limit number of emails processed
-s 2024-01-01 -e 2024-01-31 -m 50

# Enable verbose logging
-s 2024-01-01 -e 2024-01-31 -v
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

You can use Gmail's powerful search syntax with the `-q` parameter:

```
# From specific sender
-q "from:example@gmail.com"

# Subject contains specific text
-q "subject:invoice"

# Multiple conditions
-q "from:bank@example.com subject:statement"

# Has attachments (default behavior)
-q "has:attachment"
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

Downloaded PDFs are organized with descriptive filenames in the `downloads/` directory (viewable in PyCharm's Project explorer):

```
downloads/
├── 20240115_143022_bank_statement.pdf
├── 20240116_091545_company_invoice.pdf
└── 20240117_162330_utility_bill.pdf
```

Filename format: `YYYYMMDD_HHMMSS_sender_filename.pdf`

## Configuration

### Environment Variables in PyCharm

Configure environment variables in your Run Configuration:

1. Go to `Run` → `Edit Configurations`
2. Select your run configuration
3. Click the folder icon next to `Environment variables`
4. Add variables:
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to OAuth2 credentials JSON file
   - `DOWNLOAD_DIR`: Default download directory (default: `./downloads`)
   - `EMAIL_QUERY`: Default email search query (default: `has:attachment`)

### Configuration File (Alternative)

Create a `.env` file in the project root (viewable in PyCharm's Project explorer):

```env
GOOGLE_APPLICATION_CREDENTIALS=./credentials.json
DOWNLOAD_DIR=./downloads
EMAIL_QUERY=has:attachment
```

PyCharm will automatically detect and use these environment variables.

## Logging

The program creates detailed logs:
- View `pdf_fetcher.log` in PyCharm's Project explorer
- Console output appears in the Run panel at the bottom
- Enable verbose output by adding the `-v` parameter in Run Configuration

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

## Troubleshooting in PyCharm

### Common Issues

1. **Authentication Error**: 
   - Ensure your credentials file is correct and in the project directory
   - Verify the Gmail API is enabled in Google Cloud Console
   - Check the Run panel output for specific error messages

2. **No PDFs Found**: 
   - Review your date range parameters in Run Configuration
   - Verify your search query syntax
   - Check the log file in the Project explorer

3. **Permission Denied**: 
   - Ensure PyCharm has write permissions to the download directory
   - Try using a relative path like `./downloads`

4. **Rate Limit Exceeded**: 
   - The Gmail API has rate limits
   - Reduce the date range or max results parameter
   - Wait a few minutes before retrying

### PyCharm-Specific Issues

1. **Virtual Environment Not Detected**:
   - Go to `File` → `Settings` (or `PyCharm` → `Preferences` on macOS)
   - Navigate to `Project` → `Python Interpreter`
   - Click the gear icon and manually select the `venv` folder's Python interpreter
   - Look for `venv/bin/python` (macOS/Linux) or `venv\Scripts\python.exe` (Windows)

2. **Run Configuration Not Working**:
   - Go to `Run` → `Edit Configurations`
   - Remove the problematic configuration
   - Right-click the file (`run_web.py` or `main.py`) and select `Run` to recreate it

3. **Terminal Not Using Virtual Environment**:
   - Check for "(venv)" prefix in the terminal prompt
   - Close and reopen PyCharm if missing
   - Verify Python Interpreter is correctly configured

4. **Import Errors Despite Installing Packages**:
   - Verify correct interpreter is selected in Settings
   - Open PyCharm's terminal and run: `pip install -r requirements.txt`
   - Try `File` → `Invalidate Caches / Restart...`

5. **Web Server Not Starting**:
   - Check if port 5000 is already in use
   - View the Run panel for error messages
   - Ensure Flask is installed: check `requirements.txt` installation

### Viewing Logs

- Open `pdf_fetcher.log` in PyCharm's Project explorer for detailed error information
- Use the Run panel at the bottom to see real-time console output
- Right-click on log file → `Open In` → `Terminal` to tail the log

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.