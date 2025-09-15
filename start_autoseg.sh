#!/bin/bash

# Advanced Auto Segmenter 启动脚本 (Linux/macOS)

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================"
echo -e "   Advanced Auto Segmenter 启动器"
echo -e "========================================${NC}"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}[错误] 未找到Python，请先安装Python 3.8或更高版本${NC}"
    echo "Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "macOS: brew install python3"
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi

echo -e "${GREEN}[信息] Python已安装${NC}"
$PYTHON_CMD --version

# 检查是否在正确目录
if [ ! -f "autoseg.py" ]; then
    echo -e "${RED}[错误] 未找到autoseg.py文件，请确保在正确目录运行此脚本${NC}"
    exit 1
fi

echo -e "${BLUE}[信息] 正在检查依赖库...${NC}"

# 检查依赖库
if ! $PYTHON_CMD -c "import sys; sys.path.insert(0, '.'); from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" 2>/dev/null; then
    echo -e "${YELLOW}[警告] 缺少必要的依赖库${NC}"
    echo -e "${BLUE}[信息] 正在尝试自动安装依赖库...${NC}"
    echo
    
    echo "安装 faster-whisper..."
    $PIP_CMD install faster-whisper
    
    echo "安装 ffmpeg-python..."
    $PIP_CMD install ffmpeg-python
    
    echo "安装 pydub..."
    $PIP_CMD install pydub
    
    echo "安装 torch..."
    $PIP_CMD install torch
    
    echo "安装 ttkthemes (可选，用于更好的界面主题)..."
    $PIP_CMD install ttkthemes
    
    echo
    echo -e "${BLUE}[信息] 依赖库安装完成，正在重新检查...${NC}"
    if ! $PYTHON_CMD -c "import sys; sys.path.insert(0, '.'); from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" 2>/dev/null; then
        echo -e "${RED}[错误] 依赖库安装失败，请手动安装${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}[信息] 所有依赖库已就绪${NC}"
echo -e "${BLUE}[信息] 正在启动 Advanced Auto Segmenter...${NC}"
echo

# 启动应用程序
$PYTHON_CMD autoseg.py

# 检查退出状态
if [ $? -ne 0 ]; then
    echo
    echo -e "${RED}[错误] 程序异常退出${NC}"
    echo "请检查logs/autoseg.log文件获取详细错误信息"
fi
