@echo off
:: Kiểm tra quyền admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo Requesting administrator privileges...
    :: Tự động yêu cầu quyền admin
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: Lấy đường dẫn thư mục hiện tại
cd /d "%~dp0"

:: Kiểm tra môi trường ảo
if exist "env\Scripts\python.exe" (
    set PYTHON_PATH=env\Scripts\python.exe
    echo Using virtual environment Python
) else (
    set PYTHON_PATH=python
    echo Using system Python
)

:: Chạy ứng dụng với minimize
start "" /min %PYTHON_PATH% src\autoLogin_v2.py

echo Application started with admin privileges!
timeout /t 2 >nul
exit
