@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   OpenClaw 主从Agent无限迭代架构 v1.0
echo ========================================
echo.
echo 正在启动...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖是否安装
pip show zhipuai >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装依赖...
    pip install -r requirements.txt
)

REM 运行主程序
python master_slave_iterate.py

pause
