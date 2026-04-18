# -*- coding: utf-8 -*-
"""
MiroLaw - Standalone Launcher

Entry point for packaged executable
"""

import sys
import os
import io
import webbrowser
import threading
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


def get_resource_path(relative_path):
    """Get resource path (PyInstaller compatible)"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent / relative_path


def open_browser(url, delay=2):
    """Open browser after delay"""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    """Main entry point"""
    import uvicorn

    # Set working directory
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    print()
    print("=" * 50)
    print("   MiroLaw v0.5.0")
    print("   E-commerce Compliance Risk Prediction")
    print("=" * 50)
    print()
    print("  Starting service...")
    print()

    # Start browser
    browser_thread = threading.Thread(
        target=open_browser,
        args=("http://localhost:8000", 3),
        daemon=True
    )
    browser_thread.start()

    # Start server
    print("  Service: http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print()
    print("  Press Ctrl+C to stop")
    print()

    try:
        uvicorn.run(
            "src.api:app",
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=False,
        )
    except KeyboardInterrupt:
        print()
        print("Service stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
