# Advanced Auto Segmenter 启动说明

## 🚀 一键启动（推荐）

### 创建桌面快捷方式
```
双击运行 "创建桌面快捷方式.py"
```
- ✅ 自动检测操作系统
- ✅ 在桌面创建快捷方式
- ✅ 一键启动，无需记忆命令

## 快捷启动方式

本目录提供了多种启动方式，请根据您的操作系统选择合适的方法：

### 🖥️ Windows 用户

#### 方法1：双击批处理文件（推荐）
```
双击 "启动AutoSeg.bat" 文件
```
- ✅ 自动检查Python和依赖库
- ✅ 自动安装缺失的依赖库
- ✅ 提供详细的错误信息
- ✅ 中文界面友好

#### 方法2：使用Python启动器
```
双击 "AutoSeg快捷方式.py" 文件
```
- ✅ 跨平台兼容
- ✅ 彩色输出（部分Windows版本）
- ✅ 智能依赖管理

### 🐧 Linux 用户

#### 方法1：使用Shell脚本（推荐）
```bash
./start_autoseg.sh
```
- ✅ 彩色终端输出
- ✅ 自动检测Python3
- ✅ 自动安装依赖库

#### 方法2：使用Python启动器
```bash
python3 AutoSeg快捷方式.py
```

### 🍎 macOS 用户

#### 方法1：使用Shell脚本
```bash
./start_autoseg.sh
```

#### 方法2：使用Python启动器
```bash
python3 AutoSeg快捷方式.py
```

### 📱 通用方法（所有系统）

#### 直接运行Python文件
```bash
python autoseg.py
```
或
```bash
python3 autoseg.py
```

## 🔧 系统要求

### 必需软件
- **Python 3.8+** - [下载地址](https://www.python.org/downloads/)
- **FFmpeg** - 用于音视频处理
  - Windows: [下载地址](https://ffmpeg.org/download.html)
  - Linux: `sudo apt install ffmpeg` (Ubuntu/Debian)
  - macOS: `brew install ffmpeg`

### Python依赖库
启动器会自动安装以下依赖库：

#### 必需依赖
- `faster-whisper` - Whisper语音识别引擎
- `ffmpeg-python` - FFmpeg Python接口
- `pydub` - 音频处理库
- `torch` - PyTorch深度学习框架

#### 可选依赖
- `ttkthemes` - 更美观的GUI主题

## 🚀 首次使用步骤

1. **确保Python已安装**
   ```bash
   python --version
   # 或
   python3 --version
   ```

2. **选择启动方式**
   - Windows: 双击 `启动AutoSeg.bat`
   - Linux/macOS: 运行 `./start_autoseg.sh`

3. **等待依赖库安装**
   - 首次运行会自动安装所需依赖库
   - 安装过程可能需要几分钟，请耐心等待

4. **开始使用**
   - 应用程序启动后，按照界面提示操作
   - 首先加载模型，然后选择音视频文件进行处理

## 🐛 故障排除

### 常见问题

#### 1. Python未找到
**错误**: `'python' 不是内部或外部命令`
**解决**: 
- 安装Python 3.8或更高版本
- 确保Python已添加到系统PATH

#### 2. FFmpeg未找到
**错误**: `FFmpeg 未找到`
**解决**:
- 安装FFmpeg并添加到系统PATH
- Windows用户可下载便携版解压到程序目录

#### 3. 依赖库安装失败
**错误**: 各种pip安装错误
**解决**:
```bash
# 升级pip
python -m pip install --upgrade pip

# 手动安装依赖
pip install faster-whisper ffmpeg-python pydub torch
```

#### 4. CUDA相关错误
**错误**: CUDA版本不兼容
**解决**:
- 在模型配置中选择"CPU"设备
- 或安装对应的CUDA版本

### 查看日志
程序运行时会在 `logs/autoseg.log` 文件中记录详细日志，遇到问题时可查看此文件获取更多信息。

## 📞 获取帮助

如果遇到问题：
1. 查看 `logs/autoseg.log` 日志文件
2. 确认系统要求是否满足
3. 尝试手动安装依赖库
4. 检查网络连接（下载模型需要）

## 🎯 使用提示

1. **首次使用建议选择较小的模型**（如"base"）进行测试
2. **大文件处理时间较长**，请耐心等待
3. **GPU加速**需要NVIDIA显卡和CUDA支持
4. **支持多种格式**：MP4, MP3, WAV, M4A, FLAC等
5. **可导出字幕文件**：支持TXT和SRT格式
