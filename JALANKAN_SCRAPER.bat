@echo off
title LinkedIn Planner Scraper Indonesia
color 0b

echo ===================================================================
echo     LINKEDIN LOKER PLANNER SCRAPER (INDONESIA)
echo ===================================================================
echo.

cd /d "%~dp0"

echo [*] Memeriksa Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di sistem Anda!
    echo Silakan install Python 3.10+ terlebih dahulu.
    pause
    exit /b
)

echo.
python main.py

echo.
echo ===================================================================
echo  Proses selesai! Tekan sembarang tombol untuk menutup...
echo ===================================================================
pause >nul
