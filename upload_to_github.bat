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

REM 檢查是否有更改需要提交
git status | findstr /C:"nothing to commit" >nul
if %ERRORLEVEL% == 0 (
    echo 沒有檔案需要提交，直接進行推送...
) else (
    REM 提交更改
    :input_commit_message
    set "commit_msg="
    set /p commit_msg=請輸入提交信息（默認為"更新專案文件"）: 
    if "%commit_msg%"=="" (
        set "commit_msg=更新專案文件"
    )
    
    echo 提交更改...
    git commit -m "%commit_msg%"
    if %ERRORLEVEL% neq 0 (
        echo 提交信息不能為空，請重新輸入
        goto input_commit_message
    )
)

REM 推送到GitHub
echo 推送到GitHub...
git push -u origin master
if %ERRORLEVEL% neq 0 (
    echo.
    echo 檢測到遠端倉庫有新的更改，嘗試同步...
    git pull origin master
    if %ERRORLEVEL% neq 0 (
        echo 嘗試使用 --allow-unrelated-histories 選項...
        git pull origin master --allow-unrelated-histories
        if %ERRORLEVEL% neq 0 (
            echo.
            echo 嘗試推送到main分支...
            git pull origin main --allow-unrelated-histories
            git push -u origin main
            if %ERRORLEVEL% neq 0 (
                echo.
                echo 錯誤: 無法推送到GitHub。
                echo 請嘗試以下步驟:
                echo 1. 手動執行: git pull origin master --allow-unrelated-histories
                echo 2. 解決所有衝突後重新運行此腳本
                echo 3. 如果仍然失敗，請確保您的GitHub憑證設置正確
                pause
                exit /b 1
            )
        ) else (
            git push -u origin master
        )
    ) else (
        git push -u origin master
    )
)

echo.
echo 成功! 專案已上傳到 https://github.com/aken1023/macroinsight.git
echo.
pause