@echo off
cd /d "%~dp0"
title AI ライティングスタジオ

where python >nul 2>nul
if errorlevel 1 (
    echo [エラー] Python が見つかりません。
    echo   https://www.python.org/downloads/ からインストールしてください。
    echo   インストール時に "Add python.exe to PATH" のチェックを忘れずに。
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo 初回セットアップを実行します。数分かかります...
    echo.
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [エラー] セットアップに失敗しました。
        pause
        exit /b 1
    )
    echo.
    echo セットアップが完了しました。
    echo.
)

if not exist ".env" (
    echo ------------------------------------------------------------
    echo  [注意] .env がありません。API キーは画面左のサイドバーから
    echo         入力してください。
    echo         毎回の入力を省くには、.env.example をコピーして .env を
    echo         作り、GEMINI_API_KEY にキーを設定します。
    echo ------------------------------------------------------------
    echo.
)

echo AI ライティングスタジオを起動しています...
echo   ブラウザが自動で開きます ^(http://localhost:8501^)
echo   終了するには、このウィンドウで Ctrl + C を押してください。
echo.

.venv\Scripts\python.exe -m streamlit run app.py

echo.
echo アプリを終了しました。
pause
