@echo off
setlocal enabledelayedexpansion

:: AutoSeg 快捷安装器 - 简单版
:: 将当前目录添加到用户PATH，实现autoseg命令全局访问

title AutoSeg 快捷安装器

chcp 65001 >nul 2>&1

echo.
echo ========================================
echo      AutoSeg 快捷安装器 (简单版)
echo ========================================
echo.
echo 此工具将当前目录添加到您的用户PATH环境变量中，
echo 使您能够从任意位置通过 "autoseg" 命令启动应用程序。
echo.

:: 获取当前目录
set "CURRENT_DIR=%~dp0"
set "CURRENT_DIR=!CURRENT_DIR:~0,-1!"

echo 当前AutoSeg目录: !CURRENT_DIR!
echo.

:: 检查必要文件
if not exist "autoseg.py" (
    echo [错误] 当前目录中未找到 autoseg.py 文件
    echo 请在AutoSeg程序目录中运行此脚本
    pause
    exit /b 1
)

if not exist "autoseg.bat" (
    echo [错误] 当前目录中未找到 autoseg.bat 文件
    echo 请确保所有必要文件都存在
    pause
    exit /b 1
)

:: 检查是否已在PATH中
for %%i in (autoseg.bat) do set "FOUND_IN_PATH=%%~$PATH:i"
if defined FOUND_IN_PATH (
    echo [信息] autoseg命令已可用: !FOUND_IN_PATH!
    echo.
    echo 测试命令:
    autoseg.bat --help 2>nul || echo   运行 "autoseg" 启动应用程序
    echo.
    echo 如需重新安装，请先运行卸载器
    pause
    exit /b 0
)

:: 确认安装
set /p "confirm=是否将当前目录添加到PATH环境变量? (Y/n): "
if /i "!confirm!"=="n" (
    echo [信息] 安装已取消
    pause
    exit /b 0
)

echo.
echo [信息] 正在添加到用户PATH环境变量...

:: 读取当前用户PATH
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"

:: 检查是否已存在
echo !USER_PATH! | findstr /I /C:"!CURRENT_DIR!" >nul
if not errorlevel 1 (
    echo [信息] 目录已在PATH中，无需重复添加
    goto :test_installation
)

:: 添加到PATH
if defined USER_PATH (
    set "NEW_PATH=!USER_PATH!;!CURRENT_DIR!"
) else (
    set "NEW_PATH=!CURRENT_DIR!"
)

reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul 2>&1
if errorlevel 1 (
    echo [错误] 无法修改PATH环境变量
    echo.
    echo 请手动操作:
    echo 1. Win + R 打开运行对话框
    echo 2. 输入 sysdm.cpl 回车
    echo 3. 点击"环境变量"按钮
    echo 4. 在用户变量中编辑PATH
    echo 5. 添加目录: !CURRENT_DIR!
    pause
    exit /b 1
)

echo [成功] 已添加到用户PATH环境变量

:: 通知系统PATH变更 (广播消息)
echo [信息] 正在通知系统更新环境变量...

:: 使用PowerShell广播环境变量更改
powershell -Command "Add-Type -TypeDefinition 'using System; using System.Runtime.InteropServices; public class Win32 { [DllImport(\"user32.dll\")] public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint fuFlags, uint uTimeout, out UIntPtr lpdwResult); }'; $HWND_BROADCAST = [IntPtr]0xffff; $WM_SETTINGCHANGE = 0x1a; $result = 0; [Win32]::SendMessageTimeout($HWND_BROADCAST, $WM_SETTINGCHANGE, [UIntPtr]::Zero, 'Environment', 2, 5000, [ref]$result)" >nul 2>&1

:test_installation
echo.
echo [信息] 正在测试安装...

:: 刷新当前会话的环境变量
set "PATH=%PATH%;!CURRENT_DIR!"

:: 测试命令是否可用
autoseg.bat >nul 2>&1
if errorlevel 1 (
    echo [警告] 命令测试失败，可能需要重启命令提示符
) else (
    echo [成功] autoseg命令已可用！
)

:: 创建卸载脚本
echo.
echo [信息] 正在创建卸载脚本...
(
echo @echo off
echo setlocal enabledelayedexpansion
echo.
echo title AutoSeg 卸载器
echo echo 正在从PATH中移除AutoSeg目录...
echo.
echo :: 读取用户PATH
echo for /f "tokens=2*" %%%%A in ^('reg query "HKCU\Environment" /v PATH 2^^^>nul'^) do set "USER_PATH=%%%%B"
echo.
echo :: 移除目录
echo set "NEW_PATH=^^!USER_PATH:!CURRENT_DIR!;=^^!"
echo set "NEW_PATH=^^!NEW_PATH:;!CURRENT_DIR!=^^!"
echo set "NEW_PATH=^^!NEW_PATH:!CURRENT_DIR!=^^!"
echo.
echo :: 更新注册表
echo reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "^^!NEW_PATH^^!" /f ^^^>nul 2^^^>^^^&1
echo if errorlevel 1 ^(
echo     echo [错误] 无法修改PATH环境变量
echo ^) else ^(
echo     echo [成功] AutoSeg已从PATH中移除
echo     echo [提示] 请重启命令提示符使更改生效
echo ^)
echo.
echo pause
) > "uninstall_autoseg.bat"

echo [成功] 卸载脚本已创建: uninstall_autoseg.bat

echo.
echo ========================================
echo           安装完成！
echo ========================================
echo.
echo 现在您可以：
echo.
echo 方式1 (推荐): 重新打开命令提示符或PowerShell
echo          然后在任意位置输入 "autoseg"
echo.
echo 方式2: 在当前窗口中直接测试
echo          输入: autoseg
echo.
echo 方式3: 注销并重新登录以确保环境变量生效
echo.
echo 测试安装是否成功:
echo   命令提示符中输入: autoseg
echo   PowerShell中输入: .\autoseg.ps1
echo.

:: 提供立即测试选项
set /p "test_now=是否现在测试autoseg命令? (Y/n): "
if /i not "!test_now!"=="n" (
    echo.
    echo [测试] 执行 autoseg 命令:
    echo ----------------------------------------
    autoseg
)

echo.
pause
