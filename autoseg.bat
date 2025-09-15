@echo off
setlocal enabledelayedexpansion

title AutoSeg - 音视频智能分段工具

chcp 65001 >nul 2>&1

echo.
echo ========================================
echo    AutoSeg - 音视频智能分段工具
echo ========================================
echo.

:: 获取当前目录
set "AUTOSEG_DIR=%~dp0"
set "AUTOSEG_DIR=!AUTOSEG_DIR:~0,-1!"

echo 安装路径: !AUTOSEG_DIR!
echo.

:: 切换到脚本目录
cd /d "!AUTOSEG_DIR!" 2>nul
if errorlevel 1 (
    echo [错误] 无法访问AutoSeg目录
    pause
    exit /b 1
)

:: 检查主程序文件
if not exist "autoseg.py" (
    echo [错误] 未找到主程序文件 autoseg.py
    pause
    exit /b 1
)

:: 检查Python
echo [信息] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请安装Python 3.8+
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [信息] %%i

:: 检查依赖库
echo [信息] 检查依赖库...
python -c "from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" >nul 2>&1

if errorlevel 1 (
    echo [警告] 发现缺少依赖库
    echo.
    set /p "install_deps=是否自动安装依赖库? (Y/n): "
    
    if /i "!install_deps!"=="n" (
        echo [信息] 跳过依赖库安装
        pause
        exit /b 1
    )
    
    echo [信息] 正在安装依赖库...
    pip install faster-whisper ffmpeg-python pydub torch ttkthemes
    
    echo [信息] 重新检查依赖库...
    python -c "from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" >nul 2>&1
    if errorlevel 1 (
        echo [错误] 依赖库安装失败
        pause
        exit /b 1
    )
)

echo [信息] 环境检查完成
echo [信息] 正在启动AutoSeg应用程序...
echo.

:: 启动主程序
python "autoseg.py"

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    if exist "logs\autoseg.log" (
        echo 详细错误信息请查看: logs\autoseg.log
    )
    pause
)

endlocal
