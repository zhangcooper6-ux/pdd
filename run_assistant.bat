@echo off
chcp 65001 >nul
echo ===================================================
echo     🚀 启动 全域电商经营助手 (Omnichannel Commerce)
echo ===================================================
echo.

REM 检查依赖并运行主程序
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    set "PY_EXE=python"
)

"%PY_EXE%" main.py %*

echo.
pause
