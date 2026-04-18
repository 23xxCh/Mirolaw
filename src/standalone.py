# -*- coding: utf-8 -*-
"""
电商合规哨兵 - 独立启动器

用于打包为 exe 后的启动入口
"""

import sys
import os
import webbrowser
import threading
import time
from pathlib import Path


def get_resource_path(relative_path):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        return Path(sys._MEIPASS) / relative_path
    # 开发环境路径
    return Path(__file__).parent.parent / relative_path


def open_browser(url, delay=2):
    """延迟打开浏览器"""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    """主入口"""
    import uvicorn

    # 设置工作目录
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    # 静态文件目录
    static_dir = get_resource_path("frontend/public")

    print()
    print("=" * 50)
    print("   电商合规哨兵 v0.5.0")
    print("   E-commerce Compliance Risk Prediction System")
    print("=" * 50)
    print()
    print("  正在启动服务...")
    print()

    # 启动浏览器
    browser_thread = threading.Thread(
        target=open_browser,
        args=("http://localhost:8000", 3),
        daemon=True
    )
    browser_thread.start()

    # 启动服务
    print("  服务地址: http://localhost:8000")
    print("  API文档:  http://localhost:8000/docs")
    print()
    print("  按 Ctrl+C 停止服务")
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
        print("服务已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
