# AutoSeg 快捷启动指南 🚀

**现在支持全局 `autoseg` 命令！**

## 💡 一键安装命令行工具

1. **双击运行** `setup_autoseg_command.bat`
2. 按提示确认安装
3. **重新打开**命令提示符或PowerShell  
4. 在**任意位置**输入 `autoseg` 即可启动！

```cmd
C:\> autoseg
C:\Users\> autoseg  
D:\Projects\> autoseg
```

---

## 📋 所有启动方式

### 🔥 方式1: 全局命令 (推荐)
```cmd
autoseg              # 在任意位置启动
```

### 🖱️ 方式2: 双击启动
- `autoseg.bat` - 新的快速启动器
- `启动AutoSeg.bat` - 原始启动器  
- `AutoSeg快捷方式.py` - Python启动器

### 💻 方式3: PowerShell脚本
```powershell
.\autoseg.ps1           # 正常启动
.\autoseg.ps1 -Help     # 显示帮助
.\autoseg.ps1 -Version  # 版本信息
.\autoseg.ps1 -NoCheck  # 跳过依赖检查
```

### 🖥️ 方式4: 桌面快捷方式
运行 `创建桌面快捷方式.py` 创建桌面图标

---

## ⚡ 核心特性

- ✅ **自动依赖管理** - 自动检查和安装依赖库
- ✅ **智能环境检测** - Python、GPU环境自动识别
- ✅ **多启动方式** - 命令行、GUI、脚本多选择
- ✅ **详细日志** - 完整的错误诊断和调试信息
- ✅ **GPU加速** - 支持NVIDIA CUDA加速处理

---

## 🛠️ 管理工具

| 工具 | 功能 |
|------|------|
| `setup_autoseg_command.bat` | 🔧 安装全局命令 |
| `verify_autoseg.bat` | ✅ 验证安装状态 |
| `创建桌面快捷方式.py` | 🖥️ 创建桌面图标 |
| `uninstall_autoseg.bat` | 🗑️ 卸载工具 |

---

## 🎯 快速开始

### 新用户
1. 运行 `setup_autoseg_command.bat` 安装命令
2. 运行 `verify_autoseg.bat` 验证安装
3. 命令行输入 `autoseg` 启动应用

### 日常使用
```cmd
autoseg    # 一键启动，简单快捷！
```

---

## 🔍 故障排除

### 命令未找到
```cmd
# 重新打开命令提示符，或使用完整路径
"C:\path\to\autoseg\autoseg.bat"
```

### 依赖库问题
所有启动器都会自动提示安装以下依赖：
- `faster-whisper` - Whisper语音识别
- `ffmpeg-python` - 音频处理
- `pydub` - 音频操作
- `torch` - 深度学习框架
- `ttkthemes` - 界面主题

### Python环境
```cmd
python --version    # 需要 3.8+
pip --version       # 确保pip可用
```

---

## 📊 功能亮点

🎵 **多格式支持** - MP3/MP4/WAV/FLAC等
🤖 **AI语音识别** - 基于Whisper模型
✂️ **智能分段** - 自动语音分割  
⚡ **GPU加速** - NVIDIA显卡加速
📁 **多种导出** - TXT/SRT字幕文件
🎧 **音频预览** - 分段播放功能

---

## 📞 技术支持

📋 **日志位置**: `logs/autoseg.log`
🔧 **环境检查**: 运行 `verify_autoseg.bat`
💡 **获取帮助**: `autoseg.ps1 -Help`

---

**现在就试试在任意位置输入 `autoseg` 启动这个强大的音视频智能分段工具吧！** 🎉
