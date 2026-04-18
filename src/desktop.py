# -*- coding: utf-8 -*-
"""
MiroLaw - Desktop Application

Standalone desktop application with native window
"""

import sys
import os
import io
import threading
import time
import webview

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# Version
VERSION = "0.6.0"


class Api:
    """JavaScript API bridge"""

    def get_version(self):
        return VERSION

    def open_external(self, url):
        import webbrowser
        webbrowser.open(url)


def start_server():
    """Start FastAPI server in background thread"""
    import uvicorn

    # Suppress uvicorn logs
    import logging
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    uvicorn.run(
        "src.api:app",
        host="127.0.0.1",
        port=8765,
        log_level="warning",
        access_log=False,
    )


def main():
    """Main entry point"""
    print(f"MiroLaw v{VERSION} - Desktop Application")
    print("Starting server...")

    # Start server in background
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    print("Creating window...")

    # Create API bridge
    api = Api()

    # Create desktop window
    window = webview.create_window(
        title=f"MiroLaw v{VERSION} - 电商合规哨兵",
        url="http://127.0.0.1:8765",
        width=1400,
        height=900,
        min_size=(800, 600),
        js_api=api,
        text_select=True,
    )

    # Set window icon if available
    try:
        import platform
        if platform.system() == 'Windows':
            # Icon will be set by PyInstaller
            pass
    except:
        pass

    print("Application ready!")

    # Start webview (blocking)
    webview.start(
        debug=False,
        http_server=False,
    )

    print("Application closed")
    sys.exit(0)


if __name__ == "__main__":
    main()
