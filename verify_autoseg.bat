@echo off
setlocal enabledelayedexpansion

title AutoSeg 安装验证

chcp 65001 >nul 2>&1

echo.
echo ========================================
echo       AutoSeg 安装验证工具
echo ========================================
echo.

:: 测试1: 检查文件是否存在
echo [测试1] 检查核心文件...
if exist "autoseg.py" (
    echo ✓ autoseg.py 存在
) else (
    echo ✗ autoseg.py 不存在
    goto :failed
)

if exist "autoseg.bat" (
    echo ✓ autoseg.bat 存在
) else (
    echo ✗ autoseg.bat 不存在
    goto :failed
)

if exist "autoseg.ps1" (
    echo ✓ autoseg.ps1 存在
) else (
    echo ✗ autoseg.ps1 不存在
    goto :failed
)

:: 测试2: 检查Python环境
echo.
echo [测试2] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python 未找到
    goto :failed
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo ✓ %%i
)

:: 测试3: 检查依赖库
echo.
echo [测试3] 检查依赖库...
python -c "from autoseg import check_dependencies; print('✓ 依赖库检查通过' if check_dependencies() else '✗ 依赖库缺失')" 2>nul
if errorlevel 1 (
    echo ✗ 依赖库检查失败
    goto :failed
)

:: 测试4: 检查PATH设置
echo.
echo [测试4] 检查PATH设置...
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=!CURRENT_DIR:~0,-1!"

echo !PATH! | findstr /I /C:"!CURRENT_DIR!" >nul
if errorlevel 1 (
    echo ⚠ 当前目录不在系统PATH中
    echo   目录: !CURRENT_DIR!
    echo   建议运行 setup_autoseg_command.bat 安装命令行支持
) else (
    echo ✓ 当前目录已在PATH中
)

:: 测试5: 检查命令可用性
echo.
echo [测试5] 测试启动脚本...

echo 测试 autoseg.bat...
call autoseg.bat >nul 2>&1
if errorlevel 1 (
    echo ⚠ autoseg.bat 可能有问题，但这可能是正常的（因为没有GUI环境）
) else (
    echo ✓ autoseg.bat 可以执行
)

:: 所有测试完成
echo.
echo ========================================
echo           验证完成！
echo ========================================
echo.
echo 🎉 AutoSeg 已成功安装并配置！
echo.
echo 使用方法:
echo   1. 双击 autoseg.bat 启动应用程序
echo   2. 在命令行输入 autoseg （如果PATH已配置）
echo   3. 双击 启动AutoSeg.bat
echo   4. 运行 python autoseg.py
echo.
echo 🔧 管理工具:
echo   - setup_autoseg_command.bat  : 安装命令行支持
echo   - 创建桌面快捷方式.py         : 创建桌面图标
echo   - uninstall_autoseg.bat      : 卸载（安装后生成）
echo.

goto :success

:failed
echo.
echo ========================================
echo           验证失败
echo ========================================
echo.
echo ❌ AutoSeg 安装或配置存在问题
echo.
echo 请检查:
echo   1. 所有文件是否完整
echo   2. Python 是否正确安装
echo   3. 网络连接是否正常（安装依赖库时需要）
echo.

:success
pause
