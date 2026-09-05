@echo off
chcp 65001 >nul
echo ===================================================
echo     🚀 启动 全域电商经营助手 (Omnichannel Commerce)
echo ===================================================
echo.

REM 检查依赖并运行主程序
python main.py %*

echo.
pause
