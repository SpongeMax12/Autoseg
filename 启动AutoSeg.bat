@echo off
chcp 65001 >nul
title Advanced Auto Segmenter

echo ========================================
echo    Advanced Auto Segmenter 启动器
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] Python已安装
python --version

:: 检查是否在正确目录
if not exist "autoseg.py" (
    echo [错误] 未找到autoseg.py文件，请确保在正确目录运行此脚本
    pause
    exit /b 1
)

echo [信息] 正在检查依赖库...

:: 检查依赖库
python -c "import sys; sys.path.insert(0, '.'); from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" >nul 2>&1
if errorlevel 1 (
    echo [警告] 缺少必要的依赖库
    echo [信息] 正在尝试自动安装依赖库...
    echo.
    
    echo 安装 faster-whisper...
    pip install faster-whisper
    
    echo 安装 ffmpeg-python...
    pip install ffmpeg-python
    
    echo 安装 pydub...
    pip install pydub
    
    echo 安装 torch...
    pip install torch
    
    echo 安装 ttkthemes (可选，用于更好的界面主题)...
    pip install ttkthemes
    
    echo.
    echo [信息] 依赖库安装完成，正在重新检查...
    python -c "import sys; sys.path.insert(0, '.'); from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)"
    if errorlevel 1 (
        echo [错误] 依赖库安装失败，请手动安装
        pause
        exit /b 1
    )
)

echo [信息] 所有依赖库已就绪
echo [信息] 正在启动 Advanced Auto Segmenter...
echo.

:: 启动应用程序
python autoseg.py

:: 如果程序异常退出，显示错误信息
if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，错误代码: %errorlevel%
    echo 请检查logs/autoseg.log文件获取详细错误信息
    pause
)
