#!/usr/bin/env python3
"""
Web interface launcher for Gmail PDF Fetcher
"""
import sys
import webbrowser
import time
from pathlib import Path

def main():
    """Launch the web interface"""
    print("🚀 Starting Gmail PDF Fetcher Web Interface...")
    print("📁 Working directory:", Path.cwd())
    
    # Import and run the Flask app
    try:
        from app import app
        print("✅ Flask app loaded successfully")
        print("🌐 Opening web browser...")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5000')
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        print("🎯 Web interface available at: http://localhost:5000")
        print("📧 Make sure you have your Gmail credentials configured!")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Run the Flask app
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"❌ Error importing Flask app: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
