#!/usr/bin/env python3
"""
Simple script to start the GoWild Flight Finder web application
"""

import subprocess
import sys
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:8000')

if __name__ == '__main__':
    print("🚀 Starting GoWild Flight Finder Web Application...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌐 Opening browser in 2 seconds...")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 GoWild Flight Finder stopped. Thanks for using it!")
