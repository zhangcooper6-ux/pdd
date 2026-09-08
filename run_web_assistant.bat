@echo off
chcp 65001 >nul
title 全域电商经营助手 (前后端可视化系统)
echo ========================================================================
echo        🚀 全域电商经营助手 (Omnichannel Commerce Assistant)
echo   涵盖平台: 天猫(Tmall) · 京东(JD) · 抖音(Douyin) · 拼多多(PDD)
echo   架构设计: 前后端分离 · 交互式ECharts大屏 · RESTful API
echo ========================================================================
echo.
echo [1/2] 正在启动后端 RESTful API 服务 (FastAPI + Uvicorn)...
echo [2/2] 本地可视化前端访问地址: http://127.0.0.1:8888
echo.
echo 正在自动调用浏览器打开可视化大屏...
start http://127.0.0.1:8888
echo.
if exist "%~dp0.venv\Scripts\python.exe" (
    set "PY_EXE=%~dp0.venv\Scripts\python.exe"
) else (
    set "PY_EXE=python"
)

"%PY_EXE%" server.py

pause
