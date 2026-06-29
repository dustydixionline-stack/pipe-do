@echo off
cd /d "%~dp0"
echo Installation des dependances...
pip install -r requirements.txt -q
echo.
echo Lancement du Pipe DO...
python -m streamlit run app.py
pause
