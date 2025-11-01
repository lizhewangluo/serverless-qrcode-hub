@echo off
echo Building Taokouling Float Tool with PyInstaller...

REM Check if virtual environment exists, if not create one
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller

REM Create icon directory if it doesn't exist
if not exist "app\resources" mkdir app\resources

REM Note: You should place your icon.ico file in app\resources\icon.ico
REM For now, we'll build without a custom icon

REM Build the executable
echo Building executable...
pyinstaller --onefile ^
    --windowed ^
    --name "TaokoulingFloatTool" ^
    --add-data "app;app" ^
    --hidden-import PySide6.QtCore ^
    --hidden-import PySide6.QtGui ^
    --hidden-import PySide6.QtWidgets ^
    --hidden-import requests ^
    --hidden-import dotenv ^
    --hidden-import keyboard ^
    --exclude-module matplotlib ^
    --exclude-module numpy ^
    --exclude-module scipy ^
    --exclude-module PIL ^
    --distpath dist ^
    --workpath build ^
    app\main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Executable location: dist\TaokoulingFloatTool.exe
    echo.
    echo To run the application:
    echo 1. Copy the .env.example file to %APPDATA%\tkl-float\.env
    echo 2. Edit the .env file with your API credentials
    echo 3. Double-click TaokoulingFloatTool.exe
    echo.
) else (
    echo.
    echo Build failed! Check the error messages above.
    echo.
)

pause