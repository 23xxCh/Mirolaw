# -*- coding: utf-8 -*-
"""
MiroLaw v0.7.0 - Desktop Application Builder

Build standalone Windows desktop application using PyInstaller + pywebview
"""

import PyInstaller.__main__
import os
import shutil
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# Project root
ROOT_DIR = Path(__file__).parent

# Build config
APP_NAME = "mirolaw"
VERSION = os.environ.get("BUILD_VERSION", "0.7.0")

# Entry point
ENTRY_POINT = str(ROOT_DIR / "src" / "desktop.py")

# Hidden imports
HIDDEN_IMPORTS = [
    # pywebview + tray
    "webview",
    "webview.platforms",
    "webview.platforms.winforms",
    "clr",
    "System",
    "System.Windows.Forms",
    "System.Drawing",
    "pystray",
    "PIL",
    "PIL.Image",
    "PIL.ImageDraw",
    # uvicorn
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    # fastapi
    "fastapi",
    "fastapi.responses",
    "fastapi.staticfiles",
    "fastapi.templating",
    # pydantic
    "pydantic",
    "pydantic_core",
    # starlette
    "starlette",
    "starlette.responses",
    "starlette.routing",
    "starlette.middleware",
    "starlette.staticfiles",
    "starlette.requests",
    "starlette.datastructures",
    "starlette.templating",
    # others
    "httpx",
    "httpx._transports",
    "httpx._transports.default",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "sniffio",
    "h11",
    "httptools",
    "websockets",
    "websockets.legacy",
    "websockets.legacy.server",
    "email.utils",
    "multipart",
    "multipart.multipart",
    "jinja2",
    "markupsafe",
]

# Excludes (heavy packages not needed)
EXCLUDES = [
    "matplotlib",
    "tkinter",
    "unittest",
    "test",
    "tests",
    "pytest",
    "IPython",
    "jupyter",
    "notebook",
    "torch",
    "transformers",
    "sentence_transformers",
    "faiss",
    "numpy",
    "pandas",
    "scipy",
    "PySide6",
]


def build_exe():
    """Build Windows desktop application"""

    print()
    print("=" * 60)
    print(f"  MiroLaw Desktop v{VERSION}")
    print("  Windows Application Builder (pywebview)")
    print("=" * 60)
    print()

    # Clean old build files
    for d in [ROOT_DIR / "build", ROOT_DIR / "dist", ROOT_DIR / "release"]:
        if d.exists():
            print(f"Cleaning {d}...")
            shutil.rmtree(d)

    spec_file = ROOT_DIR / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()

    # PyInstaller args
    args = [
        ENTRY_POINT,
        "--name", f"{APP_NAME}-{VERSION}-x64-Windows",
        "--onefile",
        "--noconsole",  # No console window
        "--clean",
        "--noconfirm",

        # Add data files
        "--add-data", f"{ROOT_DIR / 'frontend' / 'public'};frontend/public",

        # Collect all dependencies
        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "pydantic",
        "--collect-all", "pydantic_core",
        "--collect-all", "jinja2",
        "--collect-all", "webview",
        "--collect-all", "pystray",
        "--collect-all", "PIL",
    ]

    # Add icon if exists
    icon_path = ROOT_DIR / "assets" / "icon.ico"
    if icon_path.exists():
        args.extend(["--icon", str(icon_path)])

    # Add hidden imports
    for module in HIDDEN_IMPORTS:
        args.extend(["--hidden-import", module])

    # Exclude modules
    for module in EXCLUDES:
        args.extend(["--exclude-module", module])

    # Run PyInstaller
    print("Building desktop application...")
    print(f"Entry: {ENTRY_POINT}")
    print(f"Framework: pywebview + pystray")
    print()

    try:
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"Build error: {e}")
        return None

    # Check result
    exe_file = ROOT_DIR / "dist" / f"{APP_NAME}-{VERSION}-x64-Windows.exe"

    if exe_file.exists():
        print()
        print("=" * 60)
        print("  Build Success!")
        print("=" * 60)
        print()
        print(f"  Output: {exe_file}")
        print(f"  Size: {exe_file.stat().st_size / 1024 / 1024:.2f} MB")
        print()

        # Create release package
        release_dir = ROOT_DIR / "release"
        release_dir.mkdir(exist_ok=True)

        # Copy exe
        release_exe = release_dir / f"{APP_NAME}-{VERSION}-x64-Windows.exe"
        shutil.copy(exe_file, release_exe)

        # Copy config
        shutil.copy(ROOT_DIR / ".env.example", release_dir / ".env.example")

        # Create readme
        readme = release_dir / "README.txt"
        readme.write_text(f"""MiroLaw v{VERSION} - Desktop Application
==========================================

Usage:
1. Double-click mirolaw-{VERSION}-x64-Windows.exe
2. A desktop window opens automatically
3. Close the window or use tray icon to exit

Requirements:
- Windows 10/11 (64-bit) with WebView2 (pre-installed on most systems)
- If WebView2 is missing, the app will prompt to install it

Features:
- Risk Prediction: Detect compliance risks
- Real-time Alerts: WebSocket notifications
- Legal Search: Search laws and regulations
- Fine Prediction: Estimate potential fines
- System Tray: Minimize to tray

Configuration:
- Rename .env.example to .env and add your DeepSeek API key

Support: https://github.com/23xxCh/Mirolaw
""", encoding='utf-8')

        print(f"  Release: {release_dir}")
        return exe_file
    else:
        print("Build failed!")
        return None


if __name__ == "__main__":
    build_exe()
