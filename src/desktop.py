# -*- coding: utf-8 -*-
"""
MiroLaw v0.7.0 - Desktop Application

PySide6 (Qt6) native desktop application with embedded web view.
"""

import sys
import os
import io
import signal
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QSystemTrayIcon, QMenu,
    QSplashScreen, QMessageBox, QWidget, QVBoxLayout
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QUrl
from PySide6.QtGui import QIcon, QPixmap, QAction, QFont

VERSION = "0.7.0"
SERVER_PORT = 8765


def get_resource_path(relative_path: str) -> Path:
    """Get resource path (PyInstaller compatible)"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).parent.parent / relative_path


class BackendThread(QThread):
    """FastAPI server thread"""
    server_ready = Signal()
    server_error = Signal(str)

    def run(self):
        """Run uvicorn server"""
        try:
            import uvicorn
            import logging

            # Suppress noisy logs
            logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
            logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

            # Start server
            uvicorn.run(
                "src.api:app",
                host="127.0.0.1",
                port=SERVER_PORT,
                log_level="warning",
                access_log=False,
            )
        except Exception as e:
            self.server_error.emit(str(e))


class ServerReadyChecker(QThread):
    """Check if backend server is ready"""
    ready = Signal()

    def run(self):
        """Poll server until ready"""
        import time
        import httpx

        for _ in range(60):  # Max 30 seconds
            try:
                resp = httpx.get(f"http://127.0.0.1:{SERVER_PORT}/health/live", timeout=1)
                if resp.status_code == 200:
                    self.ready.emit()
                    return
            except Exception:
                pass
            time.sleep(0.5)

        # Timeout - still emit to show something
        self.ready.emit()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"MiroLaw v{VERSION} - \u7535\u5546\u5408\u89c4\u54e8\u5175")
        self.resize(1400, 900)
        self.setMinimumSize(800, 600)

        # Center window
        self._center_window()

        # Create web view
        self.browser = QWebEngineView()
        self.setCentralWidget(self.browser)

        # Page loading indicator
        self.browser.loadStarted.connect(self._on_load_started)
        self.browser.loadFinished.connect(self._on_load_finished)

        # Set window icon
        icon_path = get_resource_path("assets/icon.ico")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # Start backend
        self._start_backend()

    def _center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            x = (geo.width() - 1400) // 2
            y = (geo.height() - 900) // 2
            self.move(x, y)

    def _start_backend(self):
        """Start backend server and wait for ready"""
        # Start server thread
        self.backend = BackendThread()
        self.backend.server_error.connect(self._on_server_error)
        self.backend.start()

        # Wait for server ready
        self.checker = ServerReadyChecker()
        self.checker.ready.connect(self._on_server_ready)
        self.checker.start()

    def _on_server_ready(self):
        """Server is ready, load the page"""
        url = QUrl(f"http://127.0.0.1:{SERVER_PORT}")
        self.browser.setUrl(url)

    def _on_server_error(self, error_msg: str):
        """Server failed to start"""
        QMessageBox.critical(
            self,
            "\u670d\u52a1\u542f\u52a8\u5931\u8d25",
            f"\u540e\u7aef\u670d\u52a1\u542f\u52a8\u5931\u8d25:\n{error_msg}"
        )

    def _on_load_started(self):
        """Page loading started"""
        self.setWindowTitle(f"MiroLaw v{VERSION} - \u52a0\u8f7d\u4e2d...")

    def _on_load_finished(self, ok: bool):
        """Page loading finished"""
        if ok:
            self.setWindowTitle(f"MiroLaw v{VERSION} - \u7535\u5546\u5408\u89c4\u54e8\u5175")
        else:
            self.setWindowTitle(f"MiroLaw v{VERSION} - \u52a0\u8f7d\u5931\u8d25")

    def closeEvent(self, event):
        """Handle window close"""
        # Stop backend
        if hasattr(self, 'backend') and self.backend.isRunning():
            self.backend.terminate()
            self.backend.wait(3000)

        # Stop tray
        if hasattr(self, 'tray'):
            self.tray.hide()

        event.accept()


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon"""

    def __init__(self, main_window: MainWindow):
        super().__init__(main_window)
        self.main_window = main_window

        # Set icon
        icon_path = get_resource_path("assets/icon.ico")
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            # Create a default icon
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.GlobalColor.blue)
            self.setIcon(QIcon(pixmap))

        self.setToolTip(f"MiroLaw v{VERSION}")

        # Create context menu
        menu = QMenu()

        show_action = QAction("\u663e\u793a\u4e3b\u7a97\u53e3", menu)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        open_browser_action = QAction("\u5728\u6d4f\u89c8\u5668\u4e2d\u6253\u5f00", menu)
        open_browser_action.triggered.connect(self._open_browser)
        menu.addAction(open_browser_action)

        menu.addSeparator()

        quit_action = QAction("\u9000\u51fa", menu)
        quit_action.triggered.connect(self._quit_app)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

        # Double click shows window
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        """Show main window"""
        self.main_window.showNormal()
        self.main_window.activateWindow()
        self.main_window.raise_()

    def _open_browser(self):
        """Open in external browser"""
        import webbrowser
        webbrowser.open(f"http://127.0.0.1:{SERVER_PORT}")

    def _quit_app(self):
        """Quit application"""
        QApplication.quit()


class SplashScreen(QSplashScreen):
    """Application splash screen"""

    def __init__(self):
        # Create splash pixmap
        pixmap = QPixmap(500, 300)
        pixmap.fill(Qt.GlobalColor.white)

        super().__init__(pixmap)

        self.setFixedSize(500, 300)

        # Draw content
        from PySide6.QtGui import QPainter, QPen, QColor
        from PySide6.QtCore import QRectF

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background gradient
        from PySide6.QtGui import QLinearGradient
        gradient = QLinearGradient(0, 0, 0, 300)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))
        painter.fillRect(0, 0, 500, 300, gradient)

        # Title
        painter.setPen(QPen(QColor("white")))
        title_font = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(title_font)
        painter.drawText(QRectF(0, 80, 500, 50), Qt.AlignmentFlag.AlignCenter, "MiroLaw")

        # Subtitle
        sub_font = QFont("Arial", 12)
        painter.setFont(sub_font)
        painter.drawText(QRectF(0, 140, 500, 30), Qt.AlignmentFlag.AlignCenter,
                        f"v{VERSION} - E-commerce Compliance Sentinel")

        # Loading text
        load_font = QFont("Arial", 10)
        painter.setFont(load_font)
        painter.drawText(QRectF(0, 220, 500, 30), Qt.AlignmentFlag.AlignCenter,
                        "Starting services...")

        painter.end()

    def show_message(self, message: str):
        """Show loading message"""
        self.showMessage(message, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter,
                        QColor("white"))


def main():
    """Application entry point"""

    # High DPI support
    QApplication.setHighDpiScaleRoundPolicy(Qt.HighDpiScaleRoundPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setApplicationName("MiroLaw")
    app.setApplicationVersion(VERSION)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    # Show splash screen
    splash = SplashScreen()
    splash.show()
    splash.show_message("Loading application...")
    app.processEvents()

    # Create main window (but don't show yet)
    splash.show_message("Initializing backend service...")
    app.processEvents()

    window = MainWindow()

    # Create system tray
    tray = SystemTrayIcon(window)
    tray.show()
    window.tray = tray

    # When server is ready, show window and close splash
    def on_ready():
        splash.close()
        window.show()

    window.checker.ready.connect(on_ready)

    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
