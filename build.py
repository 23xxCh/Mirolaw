# -*- coding: utf-8 -*-
"""
电商合规哨兵 - Windows 可执行文件打包脚本

使用 PyInstaller 将应用打包为独立的 Windows exe 文件
"""

import PyInstaller.__main__
import os
import shutil
import sys
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent

# 打包配置
APP_NAME = "mirolaw"
VERSION = "0.5.0"

# 入口文件
ENTRY_POINT = str(ROOT_DIR / "src" / "standalone.py")

# 隐式导入
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
    # 其他
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

# 排除模块
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
    """构建 Windows 可执行文件"""

    print()
    print("=" * 60)
    print(f"  电商合规哨兵 v{VERSION}")
    print("  Windows 可执行文件打包工具")
    print("=" * 60)
    print()

    # 清理旧的构建文件
    build_dir = ROOT_DIR / "build"
    dist_dir = ROOT_DIR / "dist"
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    if build_dir.exists():
        print("清理 build 目录...")
        shutil.rmtree(build_dir)

    if dist_dir.exists():
        print("清理 dist 目录...")
        shutil.rmtree(dist_dir)

    if spec_file.exists():
        spec_file.unlink()

    # PyInstaller 参数
    args = [
        ENTRY_POINT,
        "--name", f"{APP_NAME}-{VERSION}-x64-Windows",
        "--onefile",           # 打包为单个文件
        "--console",           # 控制台模式（方便查看日志）
        "--clean",             # 清理临时文件
        "--noconfirm",         # 不询问确认

        # 添加数据文件
        "--add-data", f"{ROOT_DIR / 'frontend' / 'public'};frontend/public",

        # 收集所有依赖
        "--collect-all", "uvicorn",
        "--collect-all", "fastapi",
        "--collect-all", "starlette",
        "--collect-all", "pydantic",
        "--collect-all", "pydantic_core",
    ]

    # 添加隐式导入
    for module in HIDDEN_IMPORTS:
        args.extend(["--hidden-import", module])

    # 排除不需要的模块
    for module in EXCLUDES:
        args.extend(["--exclude-module", module])

    # 运行 PyInstaller
    print("正在打包...")
    print(f"入口: {ENTRY_POINT}")
    print()

    try:
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"打包出错: {e}")
        return None

    # 输出结果
    exe_file = dist_dir / f"{APP_NAME}-{VERSION}-x64-Windows.exe"

    if exe_file.exists():
        print()
        print("=" * 60)
        print("  打包成功!")
        print("=" * 60)
        print()
        print(f"  输出文件: {exe_file}")
        print(f"  文件大小: {exe_file.stat().st_size / 1024 / 1024:.2f} MB")
        print()

        # 创建发布包
        release_dir = ROOT_DIR / "release"
        release_dir.mkdir(exist_ok=True)

        # 复制 exe
        release_exe = release_dir / f"{APP_NAME}-{VERSION}-x64-Windows.exe"
        shutil.copy(exe_file, release_exe)

        # 复制配置文件
        shutil.copy(ROOT_DIR / ".env.example", release_dir / ".env.example")

        # 创建启动说明
        readme = release_dir / "README.txt"
        readme.write_text(f"""
电商合规哨兵 v{VERSION}
========================

使用方法:
1. 双击运行 mirolaw-{VERSION}-x64-Windows.exe
2. 等待服务启动（约5-10秒）
3. 浏览器会自动打开 http://localhost:8000
4. 如需使用智能建议功能，编辑 .env.example 为 .env 并填入 API Key

功能说明:
- 风险预测: 检测商品描述和营销文案中的合规风险
- 实时预警: WebSocket 实时推送风险预警
- 法律检索: 搜索相关法律条文
- 案例查询: 查看典型违规案例

技术支持:
- GitHub: https://github.com/23xxCh/Mirolaw
- 问题反馈: https://github.com/23xxCh/Mirolaw/issues

按 Ctrl+C 停止服务
""", encoding='utf-8')

        print(f"  发布目录: {release_dir}")
        print()

        return exe_file
    else:
        print("打包失败!")
        return None


def build_portable():
    """构建便携版（带依赖目录）"""

    print()
    print("=" * 60)
    print(f"  电商合规哨兵 v{VERSION}")
    print("  便携版打包")
    print("=" * 60)
    print()

    args = [
        ENTRY_POINT,
        "--name", APP_NAME,
        "--onedir",            # 打包为目录
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

    print("正在打包便携版...")

    try:
        PyInstaller.__main__.run(args)
    except Exception as e:
        print(f"打包出错: {e}")
        return None

    dist_dir = ROOT_DIR / "dist" / APP_NAME

    if dist_dir.exists():
        # 复制配置文件
        shutil.copy(ROOT_DIR / ".env.example", dist_dir / ".env.example")
        shutil.copy(ROOT_DIR / "config.yaml", dist_dir / "config.yaml")

        print()
        print("便携版打包成功!")
        print(f"输出目录: {dist_dir}")

        return dist_dir

    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--portable":
        build_portable()
    elif len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("用法:")
        print("  python build.py          # 打包为单个 exe 文件")
        print("  python build.py --portable  # 打包为便携版目录")
    else:
        build_exe()
