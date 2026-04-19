# -*- coding: utf-8 -*-
"""
MiroLaw v0.7.0 - Desktop Application

Uses pywebview for native window + pystray for system tray.
On Windows 10/11, WebView2 (Edge) is pre-installed.
"""

import sys
import os
import io
import threading
import time
import logging
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

VERSION = "0.7.0"
SERVER_PORT = 8765

# Setup file logging (so errors are captured even without console)
LOG_DIR = Path.home() / '.mirolaw' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'app.log'

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def wait_for_server(port: int, timeout: int = 30) -> bool:
    """Wait for server to be ready"""
    import httpx
    for i in range(timeout * 2):
        try:
            resp = httpx.get(f"http://127.0.0.1:{port}/health/live", timeout=1)
            if resp.status_code == 200:
                logger.info("Server is ready")
                return True
        except Exception:
            pass
        time.sleep(0.5)
    logger.error("Server failed to start within timeout")
    return False


def start_server(port: int):
    """Start FastAPI server"""
    import uvicorn
    import logging as _logging

    _logging.getLogger("uvicorn.access").setLevel(_logging.WARNING)

    logger.info(f"Starting server on port {port}")
    try:
        uvicorn.run(
            "src.api:app",
            host="127.0.0.1",
            port=port,
            log_level="warning",
            access_log=False,
        )
    except Exception as e:
        logger.error(f"Server error: {e}")


class ApiBridge:
    """JavaScript-Python bridge"""
    def get_version(self):
        return VERSION

    def get_log_path(self):
        return str(LOG_FILE)

    def open_external(self, url):
        import webbrowser
        webbrowser.open(url)


def run_tray_icon(window):
    """Run system tray icon in separate thread"""
    try:
        from PIL import Image, ImageDraw

        # Create a simple tray icon
        img = Image.new('RGB', (64, 64), color=(102, 126, 234))
        draw = ImageDraw.Draw(img)
        draw.text((18, 20), "ML", fill=(255, 255, 255))

        import pystray
        from pystray import MenuItem as Item

        def on_show(icon, item):
            window.show()

        def on_quit(icon, item):
            icon.stop()
            window.destroy()

        menu = pystray.Menu(
            Item('Show Window', on_show, default=True),
            Item('Quit', on_quit),
        )

        icon = pystray.Icon("mirolaw", img, f"MiroLaw v{VERSION}", menu)
        icon.run()
    except Exception as e:
        logger.warning(f"Tray icon failed: {e}")


def main():
    """Application entry point"""
    import webview

    logger.info(f"MiroLaw v{VERSION} starting")

    # Start backend server
    server_thread = threading.Thread(target=start_server, args=(SERVER_PORT,), daemon=True)
    server_thread.start()

    # Wait for server to be ready
    logger.info("Waiting for server...")
    if not wait_for_server(SERVER_PORT):
        # Server didn't start - show error window
        webview.create_window(
            title="MiroLaw - Error",
            html="""
            <html><body style="font-family:sans-serif;padding:40px;background:#fde8e8">
            <h1 style="color:#e74c3c">Server Failed to Start</h1>
            <p>The backend service could not start. Please check the log file:</p>
            <p><code>""" + str(LOG_FILE) + """</code></p>
            <p>Try running from command line to see errors:</p>
            <code>python src/desktop.py</code>
            </body></html>
            """,
            width=500,
            height=300,
        )
        webview.start()
        return

    logger.info("Creating window")

    # Create API bridge
    api = ApiBridge()

    # Create main window
    window = webview.create_window(
        title=f"MiroLaw v{VERSION} - E-commerce Compliance Sentinel",
        url=f"http://127.0.0.1:{SERVER_PORT}",
        width=1400,
        height=900,
        min_size=(800, 600),
        js_api=api,
        text_select=True,
    )

    # Start tray icon thread
    tray_thread = threading.Thread(target=run_tray_icon, args=(window,), daemon=True)
    tray_thread.start()

    logger.info("Window created, starting webview")

    # Start webview (blocking)
    webview.start(
        debug=False,
        http_server=False,
    )

    logger.info("Application closed")
    sys.exit(0)


if __name__ == "__main__":
    main()
