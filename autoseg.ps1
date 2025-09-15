# Advanced Auto Segmenter PowerShell启动器
# 使用方法: autoseg.ps1 或从任意位置调用

param(
    [switch]$Version,
    [switch]$Help,
    [switch]$NoCheck
)

# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 函数：打印彩色文本
function Write-ColorText {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    
    $colorMap = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "Cyan" = "Cyan"
        "Magenta" = "Magenta"
        "White" = "White"
        "Gray" = "Gray"
    }
    
    $consoleColor = $colorMap[$Color]
    if ($consoleColor) {
        Write-Host $Text -ForegroundColor $consoleColor
    } else {
        Write-Host $Text
    }
}

# 显示版本信息
if ($Version) {
    Write-ColorText "AutoSeg PowerShell启动器 v1.0" "Green"
    Write-ColorText "Advanced Auto Segmenter 快捷启动工具" "Cyan"
    exit 0
}

# 显示帮助信息
if ($Help) {
    Write-ColorText "AutoSeg - 音视频智能分段工具启动器" "Green"
    Write-ColorText ""
    Write-ColorText "用法:" "Yellow"
    Write-ColorText "  autoseg.ps1          - 启动AutoSeg应用程序" "White"
    Write-ColorText "  autoseg.ps1 -Help    - 显示此帮助信息" "White"  
    Write-ColorText "  autoseg.ps1 -Version - 显示版本信息" "White"
    Write-ColorText "  autoseg.ps1 -NoCheck - 跳过依赖检查直接启动" "White"
    Write-ColorText ""
    Write-ColorText "功能特性:" "Yellow"
    Write-ColorText "  • 支持多种音视频格式转录" "White"
    Write-ColorText "  • 智能语音分段" "White" 
    Write-ColorText "  • 多种AI模型支持 (Whisper)" "White"
    Write-ColorText "  • GPU/CPU加速" "White"
    Write-ColorText "  • 导出TXT/SRT字幕文件" "White"
    exit 0
}

# 主程序开始
Write-ColorText ""
Write-ColorText "========================================" "Cyan"
Write-ColorText "   AutoSeg - 音视频智能分段工具" "Green"  
Write-ColorText "========================================" "Cyan"

# 获取脚本目录 (AutoSeg安装路径)
$AutoSegPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-ColorText "安装路径: $AutoSegPath" "Gray"
Write-ColorText ""

# 切换到AutoSeg目录
try {
    Set-Location -Path $AutoSegPath -ErrorAction Stop
} catch {
    Write-ColorText "[错误] 无法访问AutoSeg目录: $AutoSegPath" "Red"
    Write-ColorText "错误详情: $($_.Exception.Message)" "Red"
    Read-Host "按回车键退出"
    exit 1
}

# 检查主程序文件
$autosegFile = Join-Path $AutoSegPath "autoseg.py"
if (-not (Test-Path $autosegFile)) {
    Write-ColorText "[错误] 未找到主程序文件: autoseg.py" "Red"
    Write-ColorText "当前目录: $(Get-Location)" "Yellow"
    Write-ColorText "请确保在正确的AutoSeg安装目录中运行" "Yellow"
    Read-Host "按回车键退出"
    exit 1
}

# 检查Python环境
Write-ColorText "[信息] 检查Python环境..." "Blue"
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python未找到"
    }
    Write-ColorText "[信息] $pythonVersion" "Green"
} catch {
    Write-ColorText "[错误] Python未安装或不在PATH中" "Red"
    Write-ColorText "请安装Python 3.8或更高版本" "Yellow"
    Write-ColorText "下载地址: https://www.python.org/downloads/" "Cyan"
    Read-Host "按回车键退出"
    exit 1
}

# 依赖检查 (除非指定 -NoCheck)
if (-not $NoCheck) {
    Write-ColorText "[信息] 检查依赖库..." "Blue"
    
    $checkResult = python -c "from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" 2>$null
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorText "[警告] 发现缺少的依赖库" "Yellow"
        Write-ColorText ""
        
        $install = Read-Host "是否自动安装依赖库? (Y/n)"
        
        if ($install -eq "n" -or $install -eq "N") {
            Write-ColorText "[信息] 跳过依赖库安装" "Yellow"
            Write-ColorText "您可以稍后运行以下命令安装:" "White"
            Write-ColorText "pip install faster-whisper ffmpeg-python pydub torch ttkthemes" "Cyan"
            Read-Host "按回车键退出"
            exit 1
        }
        
        Write-ColorText "[信息] 正在安装依赖库..." "Blue"
        pip install faster-whisper ffmpeg-python pydub torch ttkthemes
        
        Write-ColorText "[信息] 重新检查依赖库..." "Blue"
        $recheckResult = python -c "from autoseg import check_dependencies; exit(0 if check_dependencies() else 1)" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-ColorText "[错误] 依赖检查仍然失败，请手动安装" "Red"
            Read-Host "按回车键退出"
            exit 1
        }
        
        Write-ColorText "[信息] 依赖库安装完成" "Green"
    }
    
    Write-ColorText "[信息] 所有依赖库已就绪" "Green"
} else {
    Write-ColorText "[信息] 跳过依赖检查" "Yellow"
}

Write-ColorText "[信息] 正在启动AutoSeg应用程序..." "Blue"
Write-ColorText ""

# 启动主程序
try {
    python "autoseg.py"
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-ColorText ""
        Write-ColorText "[错误] 程序异常退出 (代码: $exitCode)" "Red"
        
        $logFile = Join-Path $AutoSegPath "logs\autoseg.log"
        if (Test-Path $logFile) {
            Write-ColorText "详细错误信息请查看: $logFile" "Yellow"
        }
        Write-ColorText ""
        Read-Host "按回车键退出"
        exit $exitCode
    } else {
        Write-ColorText ""
        Write-ColorText "[信息] AutoSeg已正常退出" "Green"
    }
    
} catch {
    Write-ColorText ""
    Write-ColorText "[错误] 启动失败: $($_.Exception.Message)" "Red"
    Read-Host "按回车键退出"
    exit 1
}
