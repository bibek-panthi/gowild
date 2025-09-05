#!/usr/bin/env python3
"""
GoWild Flight Finder - Auto-Start Wrapper
Starts the web application and automatically opens your browser
"""

import subprocess
import sys
import webbrowser
import time
import threading
import socket

def is_port_open(port):
    """Check if a port is already in use"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    except:
        return False

def open_browser_when_ready():
    """Wait for server to start, then open browser"""
    print("🌐 Waiting for server to start...")
    
    # Wait up to 10 seconds for server to be ready
    for i in range(20):
        if is_port_open(8000):
            print("✅ Server is ready! Opening browser...")
            webbrowser.open('http://localhost:8000')
            return
        time.sleep(0.5)
    
    print("⚠️  Server took too long to start. Please open http://localhost:8000 manually.")

if __name__ == '__main__':
    print("🚀 Starting GoWild Flight Finder...")
    print("📍 Server will be available at: http://localhost:8000")
    print("🌐 Browser will open automatically when ready")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Start browser opener in background thread
    browser_thread = threading.Thread(target=open_browser_when_ready, daemon=True)
    browser_thread.start()
    
    try:
        # Start the Flask application
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 GoWild Flight Finder stopped. Thanks for flying with us!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("💡 Try running 'python3 app.py' directly instead.")
