@echo off
IF NOT EXIST env (
    REM Create a virtual environment
    python -m venv env
)
call env\Scripts\activate
pip install -r requirements.txt
python gui2.py
pause
