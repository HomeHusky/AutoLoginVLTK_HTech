@echo off
SETLOCAL

:: Đặt vị trí cửa sổ CMD ở góc trái dưới cùng
powershell -command "&{(new-object -comobject shell.application).windows() | where-object { $_.title -eq '' } | foreach-object { $_.left = 0; $_.top = [System.Windows.SystemParameters]::PrimaryScreenHeight - 250 }}"

:: Kiểm tra nếu script đang chạy với quyền quản trị viên
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Requesting Administrator privileges...
    PowerShell -Command "Start-Process '%~f0' -Verb RunAs"
    EXIT /b
)

:: Chuyển về thư mục của script .bat
cd /d "%~dp0"

:: Kiểm tra xem Python đã được cài đặt chưa
py --version
IF %ERRORLEVEL% NEQ 0 (
    echo Python not found. Installing Python 32-bit...
    :: Tải Python 32-bit tự động từ python.org
    curl -o python_installer.exe https://www.python.org/ftp/python/3.12.1/python-3.12.1.exe
    :: Cài đặt Python 32-bit tự động, thêm Python vào PATH
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    :: Xóa file cài đặt sau khi cài xong
    del python_installer.exe
) ELSE (
    echo Python is already installed.
)

:: Kiểm tra xem môi trường ảo đã tồn tại chưa
IF EXIST "env\Scripts\activate" (
    echo Using existing virtual environment...
) ELSE (
    :: Tạo môi trường ảo mới
    echo Creating a new virtual environment...
    py -m venv env
    :: Kiểm tra xem môi trường ảo đã được tạo chưa
    IF NOT EXIST "env\Scripts\activate" (
        echo Failed to create virtual environment. Exiting...
        exit /b 1
    )
)

:: Kích hoạt môi trường ảo
call env\Scripts\activate

:: Cài đặt các thư viện cần thiết từ file requirements.txt
py -m pip install --upgrade pip
pip install -r requirements.txt

:: Chạy chương trình Python
start "" /min python src\autoLogin.py
pause
ENDLOCAL
