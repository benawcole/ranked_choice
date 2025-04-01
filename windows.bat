@echo off

cd /d %~dp0

set VENV_DIR=venv

:: Check if virtual environment exists
if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

:: Activate virtual environment
call %VENV_DIR%\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Run the script
echo Launching main.py...
python main.py