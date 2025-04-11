@echo off
chcp 65001 >nul
echo ===== MacroInsight GitHub上傳腳本 =====
echo.

REM 檢查是否安裝了Git
where git >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 錯誤: 未找到Git。請先安裝Git並確保其在PATH中。
    echo 您可以從 https://git-scm.com/downloads 下載Git。
    pause
    exit /b 1
)

REM 初始化Git倉庫（如果尚未初始化）
if not exist .git (
    echo 初始化Git倉庫...
    git init
    if %ERRORLEVEL% neq 0 (
        echo 錯誤: 無法初始化Git倉庫。
        pause
        exit /b 1
    )
)

REM 添加遠程倉庫（如果尚未添加）
git remote -v | findstr "origin" >nul
if %ERRORLEVEL% neq 0 (
    echo 添加遠程倉庫...
    git remote add origin https://github.com/aken1023/macroinsight.git
    if %ERRORLEVEL% neq 0 (
        echo 錯誤: 無法添加遠程倉庫。
        pause
        exit /b 1
    )
)

REM 添加所有文件到暫存區
echo 添加文件到暫存區...
git add .
if %ERRORLEVEL% neq 0 (
    echo 錯誤: 無法添加文件到暫存區。
    pause
    exit /b 1
)

REM 提交更改
set /p commit_msg=請輸入提交信息（默認為"更新專案文件"）: 
if "%commit_msg%"=="" set commit_msg=更新專案文件

echo 提交更改...
git commit -m "%commit_msg%"
if %ERRORLEVEL% neq 0 (
    echo 錯誤: 無法提交更改。
    pause
    exit /b 1
)

REM 推送到GitHub
echo 推送到GitHub...
git push -u origin master
if %ERRORLEVEL% neq 0 (
    echo.
    echo 嘗試推送到main分支...
    git push -u origin main
    if %ERRORLEVEL% neq 0 (
        echo.
        echo 錯誤: 無法推送到GitHub。可能需要先設置GitHub憑證。
        echo 請嘗試以下步驟:
        echo 1. 確保您已在GitHub上創建了倉庫 https://github.com/aken1023/macroinsight.git
        echo 2. 如果您使用HTTPS連接，請確保您已配置了GitHub憑證
        echo 3. 如果您使用SSH連接，請確保您已設置了SSH密鑰
        pause
        exit /b 1
    )
)

echo.
echo 成功! 專案已上傳到 https://github.com/aken1023/macroinsight.git
echo.
pause