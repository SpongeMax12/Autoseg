@echo off
setlocal enabledelayedexpansion

:: AutoSeg 系统安装器
:: 将autoseg命令添加到系统PATH，实现全局访问

title AutoSeg 系统安装器

:: 设置UTF-8编码
chcp 65001 >nul 2>&1

echo.
echo ========================================
echo       AutoSeg 系统安装器
echo ========================================
echo.
echo 此工具将安装autoseg命令到系统，使您可以从任意位置
echo 通过输入 "autoseg" 来启动应用程序。
echo.

:: 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo [提示] 建议以管理员身份运行以获得最佳体验
    echo 当前将以用户权限安装 (仅对当前用户有效)
    echo.
    set "INSTALL_SCOPE=user"
) else (
    echo [信息] 检测到管理员权限，将为所有用户安装
    echo.
    set "INSTALL_SCOPE=system"
)

:: 获取当前AutoSeg目录
set "AUTOSEG_SOURCE_DIR=%~dp0"
set "AUTOSEG_SOURCE_DIR=!AUTOSEG_SOURCE_DIR:~0,-1!"

echo 当前AutoSeg位置: !AUTOSEG_SOURCE_DIR!

:: 检查必要文件
if not exist "!AUTOSEG_SOURCE_DIR!\autoseg.py" (
    echo [错误] 未找到主程序文件 autoseg.py
    pause
    exit /b 1
)

if not exist "!AUTOSEG_SOURCE_DIR!\autoseg.bat" (
    echo [错误] 未找到启动脚本 autoseg.bat
    pause  
    exit /b 1
)

:: 选择安装方式
echo.
echo 请选择安装方式:
echo.
echo 1. 创建软链接 (推荐) - 占用空间最小，更新方便
echo 2. 复制到系统目录 - 独立安装，不依赖原目录
echo 3. 添加到PATH环境变量 - 直接使用当前位置
echo 4. 创建桌面快捷方式 - 仅创建桌面图标
echo 5. 取消安装
echo.

set /p "choice=请选择 (1-5): "

if "!choice!"=="1" goto :install_symlink
if "!choice!"=="2" goto :install_copy
if "!choice!"=="3" goto :install_path
if "!choice!"=="4" goto :install_desktop
if "!choice!"=="5" goto :cancel
goto :invalid_choice

:install_symlink
echo.
echo [信息] 正在创建软链接安装...

:: 确定安装目录
if "!INSTALL_SCOPE!"=="system" (
    set "INSTALL_DIR=C:\Program Files\AutoSeg"
    set "PATH_DIR=!INSTALL_DIR!"
) else (
    set "INSTALL_DIR=%LOCALAPPDATA%\Programs\AutoSeg"
    set "PATH_DIR=!INSTALL_DIR!"
)

:: 创建安装目录
if not exist "!INSTALL_DIR!" (
    mkdir "!INSTALL_DIR!" 2>nul
    if errorlevel 1 (
        echo [错误] 无法创建安装目录: !INSTALL_DIR!
        pause
        exit /b 1
    )
)

:: 创建软链接 (需要 Windows 10+ 或管理员权限)
echo 创建软链接到: !INSTALL_DIR!

mklink /D "!INSTALL_DIR!\autoseg_source" "!AUTOSEG_SOURCE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [警告] 无法创建目录软链接，改为复制文件方式
    goto :install_copy
)

:: 创建启动脚本
echo @echo off > "!INSTALL_DIR!\autoseg.bat"
echo call "!INSTALL_DIR!\autoseg_source\autoseg.bat" %%* >> "!INSTALL_DIR!\autoseg.bat"

goto :add_to_path

:install_copy
echo.
echo [信息] 正在复制文件安装...

:: 确定安装目录
if "!INSTALL_SCOPE!"=="system" (
    set "INSTALL_DIR=C:\Program Files\AutoSeg"
    set "PATH_DIR=!INSTALL_DIR!"
) else (
    set "INSTALL_DIR=%LOCALAPPDATA%\Programs\AutoSeg"
    set "PATH_DIR=!INSTALL_DIR!"
)

:: 创建安装目录
if not exist "!INSTALL_DIR!" (
    mkdir "!INSTALL_DIR!" 2>nul
    if errorlevel 1 (
        echo [错误] 无法创建安装目录: !INSTALL_DIR!
        pause
        exit /b 1
    )
)

echo 复制文件到: !INSTALL_DIR!

:: 复制所有文件
xcopy "!AUTOSEG_SOURCE_DIR!\*" "!INSTALL_DIR!\" /E /I /Y /Q >nul 2>&1
if errorlevel 1 (
    echo [错误] 文件复制失败
    pause
    exit /b 1
)

goto :add_to_path

:install_path
echo.
echo [信息] 正在添加到PATH环境变量...

set "PATH_DIR=!AUTOSEG_SOURCE_DIR!"
goto :add_to_path

:install_desktop
echo.
echo [信息] 正在创建桌面快捷方式...

:: 使用现有的桌面快捷方式创建器
if exist "创建桌面快捷方式.py" (
    python "创建桌面快捷方式.py"
) else (
    :: 手动创建快捷方式
    set "DESKTOP=%USERPROFILE%\Desktop"
    copy "autoseg.bat" "!DESKTOP!\AutoSeg.bat" >nul 2>&1
    if errorlevel 1 (
        echo [错误] 创建桌面快捷方式失败
    ) else (
        echo [成功] 桌面快捷方式已创建
    )
)

echo.
echo 安装完成！您可以：
echo - 双击桌面上的 AutoSeg.bat 启动应用
echo - 在文件夹中双击 autoseg.bat 启动应用
pause
exit /b 0

:add_to_path
echo 添加到PATH: !PATH_DIR!

:: 检查是否已在PATH中
echo !PATH! | findstr /I /C:"!PATH_DIR!" >nul
if not errorlevel 1 (
    echo [信息] PATH中已存在此目录，跳过添加
    goto :installation_complete
)

:: 添加到PATH
if "!INSTALL_SCOPE!"=="system" (
    :: 系统级PATH (需要管理员权限)
    for /f "tokens=2*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH 2^>nul') do set "SYSTEM_PATH=%%B"
    
    if defined SYSTEM_PATH (
        reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d "!SYSTEM_PATH!;!PATH_DIR!" /f >nul 2>&1
        if errorlevel 1 (
            echo [警告] 无法修改系统PATH，改为用户PATH
            goto :add_user_path
        ) else (
            echo [成功] 已添加到系统PATH
        )
    ) else (
        echo [警告] 无法读取系统PATH，改为用户PATH
        goto :add_user_path
    )
) else (
    :add_user_path
    :: 用户级PATH
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "USER_PATH=%%B"
    
    if defined USER_PATH (
        reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "!USER_PATH!;!PATH_DIR!" /f >nul 2>&1
    ) else (
        reg add "HKCU\Environment" /v PATH /t REG_EXPAND_SZ /d "!PATH_DIR!" /f >nul 2>&1
    )
    
    if errorlevel 1 (
        echo [错误] 无法修改用户PATH
        echo 请手动将以下目录添加到PATH环境变量：
        echo !PATH_DIR!
    ) else (
        echo [成功] 已添加到用户PATH
    )
)

:installation_complete
echo.
echo ========================================
echo           安装完成！
echo ========================================
echo.
echo 现在您可以：
echo.
echo 1. 重新打开命令提示符或PowerShell
echo 2. 在任意位置输入 "autoseg" 启动应用程序
echo 3. 或双击桌面快捷方式（如果已创建）
echo.
echo 如果命令不可用，请：
echo 1. 重启命令提示符
echo 2. 或注销并重新登录
echo 3. 或重启计算机
echo.

:: 创建卸载脚本
echo 正在创建卸载脚本...
(
echo @echo off
echo title AutoSeg 卸载器
echo echo 正在卸载AutoSeg...
if "!choice!"=="1" (
    echo rmdir /s /q "!INSTALL_DIR!" 2^>nul
) else if "!choice!"=="2" (
    echo rmdir /s /q "!INSTALL_DIR!" 2^>nul
)
echo echo 请手动从PATH环境变量中移除: !PATH_DIR!
echo echo 卸载完成
echo pause
) > "!PATH_DIR!\uninstall_autoseg.bat"

echo [信息] 卸载脚本已创建: !PATH_DIR!\uninstall_autoseg.bat
echo.
pause
exit /b 0

:invalid_choice
echo.
echo [错误] 无效选择，请重新运行安装器
pause
exit /b 1

:cancel
echo.
echo [信息] 安装已取消
pause
exit /b 0
