#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建桌面快捷方式工具
为Advanced Auto Segmenter创建桌面快捷方式
"""

import os
import sys
import platform
from pathlib import Path

def create_windows_shortcut():
    """为Windows创建桌面快捷方式"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Advanced Auto Segmenter.lnk")
        target = str(Path(__file__).parent / "启动AutoSeg.bat")
        wDir = str(Path(__file__).parent)
        icon = target
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = icon
        shortcut.Description = "Advanced Auto Segmenter - 音视频智能分段工具"
        shortcut.save()
        
        return True, f"快捷方式已创建: {path}"
        
    except ImportError:
        # 如果没有winshell，使用备用方法
        try:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.join(os.path.expanduser("~"), "桌面")
            
            shortcut_path = os.path.join(desktop, "启动AutoSeg.bat")
            target_path = str(Path(__file__).parent / "启动AutoSeg.bat")
            
            # 创建批处理文件的副本作为快捷方式
            import shutil
            shutil.copy2(target_path, shortcut_path)
            
            return True, f"快捷方式已创建: {shortcut_path}"
            
        except Exception as e:
            return False, f"创建快捷方式失败: {e}"
    
    except Exception as e:
        return False, f"创建快捷方式失败: {e}"

def create_linux_desktop_entry():
    """为Linux创建桌面快捷方式"""
    try:
        desktop_dir = Path.home() / "Desktop"
        if not desktop_dir.exists():
            desktop_dir = Path.home() / "桌面"
        
        if not desktop_dir.exists():
            desktop_dir.mkdir()
        
        desktop_file = desktop_dir / "AutoSeg.desktop"
        script_path = Path(__file__).parent / "start_autoseg.sh"
        icon_path = Path(__file__).parent / "autoseg.py"  # 使用Python文件作为图标
        
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Advanced Auto Segmenter
Comment=音视频智能分段工具
Exec=bash "{script_path}"
Icon=applications-multimedia
Path={Path(__file__).parent}
Terminal=true
Categories=AudioVideo;Audio;Video;
"""
        
        with open(desktop_file, 'w', encoding='utf-8') as f:
            f.write(desktop_content)
        
        # 设置可执行权限
        os.chmod(desktop_file, 0o755)
        
        return True, f"桌面快捷方式已创建: {desktop_file}"
        
    except Exception as e:
        return False, f"创建桌面快捷方式失败: {e}"

def create_macos_alias():
    """为macOS创建桌面别名"""
    try:
        desktop = Path.home() / "Desktop"
        script_path = Path(__file__).parent / "start_autoseg.sh"
        alias_path = desktop / "AutoSeg启动器"
        
        # 创建一个简单的shell脚本作为别名
        alias_content = f"""#!/bin/bash
cd "{Path(__file__).parent}"
./start_autoseg.sh
"""
        
        with open(alias_path, 'w', encoding='utf-8') as f:
            f.write(alias_content)
        
        os.chmod(alias_path, 0o755)
        
        return True, f"桌面别名已创建: {alias_path}"
        
    except Exception as e:
        return False, f"创建桌面别名失败: {e}"

def create_python_shortcut():
    """创建通用Python快捷方式"""
    try:
        desktop_paths = [
            Path.home() / "Desktop",
            Path.home() / "桌面",
            Path.home() / "Рабочий стол",  # Russian
            Path.home() / "Bureau",        # French
            Path.home() / "Escritorio",    # Spanish
        ]
        
        desktop = None
        for path in desktop_paths:
            if path.exists():
                desktop = path
                break
        
        if not desktop:
            desktop = Path.home() / "Desktop"
            desktop.mkdir(exist_ok=True)
        
        if platform.system() == "Windows":
            shortcut_name = "启动AutoSeg.bat"
            source_file = "启动AutoSeg.bat"
        else:
            shortcut_name = "启动AutoSeg.py"
            source_file = "AutoSeg快捷方式.py"
        
        shortcut_path = desktop / shortcut_name
        source_path = Path(__file__).parent / source_file
        
        import shutil
        shutil.copy2(source_path, shortcut_path)
        
        if platform.system() != "Windows":
            os.chmod(shortcut_path, 0o755)
        
        return True, f"快捷方式已创建: {shortcut_path}"
        
    except Exception as e:
        return False, f"创建快捷方式失败: {e}"

def main():
    """主函数"""
    print("=" * 60)
    print("   Advanced Auto Segmenter 桌面快捷方式创建器")
    print("=" * 60)
    print()
    
    system = platform.system()
    print(f"检测到操作系统: {system}")
    print()
    
    success = False
    message = ""
    
    if system == "Windows":
        print("正在为Windows创建桌面快捷方式...")
        success, message = create_windows_shortcut()
        
        if not success:
            print("尝试备用方法...")
            success, message = create_python_shortcut()
            
    elif system == "Linux":
        print("正在为Linux创建桌面快捷方式...")
        success, message = create_linux_desktop_entry()
        
        if not success:
            print("尝试备用方法...")
            success, message = create_python_shortcut()
            
    elif system == "Darwin":  # macOS
        print("正在为macOS创建桌面别名...")
        success, message = create_macos_alias()
        
        if not success:
            print("尝试备用方法...")
            success, message = create_python_shortcut()
            
    else:
        print("未知操作系统，使用通用方法...")
        success, message = create_python_shortcut()
    
    print()
    if success:
        print("✅ " + message)
        print()
        print("现在您可以:")
        print("1. 在桌面找到快捷方式并双击运行")
        print("2. 或者直接在当前目录运行启动文件")
        print()
        print("启动方式说明:")
        if system == "Windows":
            print("- 双击桌面上的快捷方式")
            print("- 或双击目录中的 '启动AutoSeg.bat'")
        else:
            print("- 双击桌面上的快捷方式")
            print("- 或在终端运行 './start_autoseg.sh'")
            print("- 或运行 'python3 AutoSeg快捷方式.py'")
    else:
        print("❌ " + message)
        print()
        print("手动创建快捷方式:")
        print("1. 复制以下文件到桌面:")
        if system == "Windows":
            print("   - 启动AutoSeg.bat")
        else:
            print("   - start_autoseg.sh")
            print("   - AutoSeg快捷方式.py")
        print("2. 双击运行即可")
    
    print()
    input("按回车键退出...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断操作")
    except Exception as e:
        print(f"\n发生错误: {e}")
        input("按回车键退出...")
