#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Auto Segmenter 快捷启动器
这是一个跨平台的Python启动器，可以在任何安装了Python的系统上运行
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def print_colored(text, color='white'):
    """打印彩色文本"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    
    if platform.system() == 'Windows':
        # Windows可能不支持ANSI颜色，直接打印
        print(text)
    else:
        print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_colored(f"[错误] Python版本过低: {version.major}.{version.minor}", 'red')
        print_colored("需要Python 3.8或更高版本", 'red')
        return False
    
    print_colored(f"[信息] Python版本: {version.major}.{version.minor}.{version.micro}", 'green')
    return True

def check_autoseg_file():
    """检查autoseg.py文件是否存在"""
    current_dir = Path(__file__).parent
    autoseg_path = current_dir / "autoseg.py"
    
    if not autoseg_path.exists():
        print_colored("[错误] 未找到autoseg.py文件", 'red')
        print_colored(f"当前目录: {current_dir}", 'yellow')
        return False
    
    print_colored(f"[信息] 找到autoseg.py: {autoseg_path}", 'green')
    return True

def install_dependencies():
    """安装依赖库"""
    dependencies = [
        "faster-whisper",
        "ffmpeg-python", 
        "pydub",
        "torch",
        "ttkthemes"  # 可选依赖
    ]
    
    print_colored("[信息] 正在安装依赖库...", 'blue')
    
    for dep in dependencies:
        try:
            print_colored(f"安装 {dep}...", 'cyan')
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print_colored(f"✓ {dep} 安装成功", 'green')
            else:
                if dep == "ttkthemes":  # 可选依赖失败不影响主程序
                    print_colored(f"⚠ {dep} 安装失败 (可选依赖)", 'yellow')
                else:
                    print_colored(f"✗ {dep} 安装失败", 'red')
                    print_colored(f"错误: {result.stderr}", 'red')
                    return False
                    
        except subprocess.TimeoutExpired:
            print_colored(f"✗ {dep} 安装超时", 'red')
            return False
        except Exception as e:
            print_colored(f"✗ {dep} 安装异常: {e}", 'red')
            return False
    
    return True

def check_dependencies():
    """检查依赖库"""
    try:
        # 添加当前目录到Python路径
        current_dir = str(Path(__file__).parent)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from autoseg import check_dependencies
        return check_dependencies()
    except ImportError as e:
        print_colored(f"[警告] 无法导入依赖检查模块: {e}", 'yellow')
        return False
    except Exception as e:
        print_colored(f"[错误] 依赖检查失败: {e}", 'red')
        return False

def start_autoseg():
    """启动AutoSeg应用程序"""
    try:
        current_dir = Path(__file__).parent
        autoseg_path = current_dir / "autoseg.py"
        
        print_colored("[信息] 正在启动 Advanced Auto Segmenter...", 'blue')
        print_colored("=" * 50, 'cyan')
        
        # 启动应用程序
        result = subprocess.run([sys.executable, str(autoseg_path)], cwd=current_dir)
        
        if result.returncode != 0:
            print_colored(f"[错误] 程序异常退出，错误代码: {result.returncode}", 'red')
            print_colored("请检查logs/autoseg.log文件获取详细错误信息", 'yellow')
            return False
            
    except KeyboardInterrupt:
        print_colored("\n[信息] 用户中断程序", 'yellow')
        return True
    except Exception as e:
        print_colored(f"[错误] 启动失败: {e}", 'red')
        return False
    
    return True

def main():
    """主函数"""
    print_colored("=" * 50, 'cyan')
    print_colored("   Advanced Auto Segmenter 快捷启动器", 'blue')
    print_colored("=" * 50, 'cyan')
    print()
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return 1
    
    # 检查autoseg.py文件
    if not check_autoseg_file():
        input("按回车键退出...")
        return 1
    
    # 检查依赖库
    print_colored("[信息] 正在检查依赖库...", 'blue')
    if not check_dependencies():
        print_colored("[警告] 缺少必要的依赖库", 'yellow')
        
        response = input("是否自动安装依赖库? (y/n): ").lower().strip()
        if response in ['y', 'yes', '是', '']:
            if not install_dependencies():
                print_colored("[错误] 依赖库安装失败", 'red')
                input("按回车键退出...")
                return 1
            
            # 重新检查依赖
            if not check_dependencies():
                print_colored("[错误] 依赖库仍然缺失，请手动安装", 'red')
                input("按回车键退出...")
                return 1
        else:
            print_colored("[信息] 跳过依赖库安装", 'yellow')
            input("按回车键退出...")
            return 1
    
    print_colored("[信息] 所有依赖库已就绪", 'green')
    print()
    
    # 启动应用程序
    if not start_autoseg():
        input("按回车键退出...")
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print_colored(f"[致命错误] {e}", 'red')
        input("按回车键退出...")
        sys.exit(1)
