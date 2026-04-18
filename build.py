# -*- coding: utf-8 -*-
"""
MiroLaw - Windows Executable Build Script

Build standalone Windows executable using PyInstaller
"""

import PyInstaller.__main__
import os
import shutil
import sys
import io
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Project root
ROOT_DIR = Path(__file__).parent

# Build config
APP_NAME = "mirolaw"
VERSION = os.environ.get("BUILD_VERSION", "0.5.1")

# Entry point
ENTRY_POINT = str(ROOT_DIR / "src" / "standalone.py")

# Hidden imports
HIDDEN_IMPORTS = [
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
    "watchfiles",
    "watchfiles.main",
]

# Excludes
EXCLUDES = [
    "matplotlib",
    "PIL",
    "tkinter",
    "unittest",
    "test",
    "tests",
    "pytest",
    "IPython",
    "jupyter",
    "notebook",
]


def build_exe():
    """Build Windows executable"""

    print()
    print("=" * 60)
    print(f"  MiroLaw v{VERSION}")
    print("  Windows Executable Builder")
    print("=" * 60)
    print()

    # Clean old build files
    build_dir = ROOT_DIR / "build"
    dist_dir = ROOT_DIR / "dist"
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    if build_dir.exists():
        print("Cleaning build directory...")
        shutil.rmtree(build_dir)

    if dist_dir.exists():
        print("Cleaning dist directory...")
        shutil.rmtree(dist_dir)

    if spec_file.exists():
        spec_file.unlink()

    # PyInstaller args
    args = [
        ENTRY_POINT,
        "--name", f"{APP_NAME}-{VERSION}-x64-Windows",
        "--onefile",
        "--console",
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
    ]

    # Add hidden imports
    for module in HIDDEN_IMPORTS:
        args.extend(["--hidden-import", module])

    # Exclude modules
    for module in EXCLUDES:
        args.extend(["--exclude-module", module])

    # Run PyInstaller
    print("Building...")
    print(f"Entry: {ENTRY_POINT}")
    print()

    try:
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"Build error: {e}")
        return None

    # Check result
    exe_file = dist_dir / f"{APP_NAME}-{VERSION}-x64-Windows.exe"

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
        readme.write_text(f"""MiroLaw v{VERSION}
========================

Usage:
1. Run mirolaw-{VERSION}-x64-Windows.exe
2. Wait for service to start (5-10 seconds)
3. Browser will open http://localhost:8000 automatically
4. For AI suggestions, rename .env.example to .env and add your API key

Features:
- Risk Prediction: Detect compliance risks in product descriptions
- Real-time Alerts: WebSocket push notifications
- Legal Search: Search relevant laws and regulations
- Case Library: View typical violation cases
- Fine Prediction: Estimate potential fines
- AI Suggestions: Generate remediation plans

Support:
- GitHub: https://github.com/23xxCh/Mirolaw
- Issues: https://github.com/23xxCh/Mirolaw/issues

Press Ctrl+C to stop the service
""", encoding='utf-8')

        print(f"  Release: {release_dir}")
        print()

        return exe_file
    else:
        print("Build failed!")
        return None


def build_portable():
    """Build portable version (with dependencies directory)"""

    print()
    print("=" * 60)
    print(f"  MiroLaw v{VERSION}")
    print("  Portable Build")
    print("=" * 60)
    print()

    args = [
        ENTRY_POINT,
        "--name", APP_NAME,
        "--onedir",
        "--clean",
        "--noconfirm",

        "--add-data", f"{ROOT_DIR / 'frontend' / 'public'};frontend/public",

        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "pydantic",
    ]

    for module in HIDDEN_IMPORTS:
        args.extend(["--hidden-import", module])

    for module in EXCLUDES:
        args.extend(["--exclude-module", module])

    print("Building portable version...")

    try:
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"Build error: {e}")
        return None

    dist_dir = ROOT_DIR / "dist" / APP_NAME

    if dist_dir.exists():
        # Copy config
        shutil.copy(ROOT_DIR / ".env.example", dist_dir / ".env.example")
        shutil.copy(ROOT_DIR / "config.yaml", dist_dir / "config.yaml")

        print()
        print("Portable build success!")
        print(f"Output: {dist_dir}")

        return dist_dir

    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--portable":
        build_portable()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python build.py          # Build single exe file")
        print("  python build.py --portable  # Build portable directory")
    else:
        build_exe()
