

@echo off
cd /d C:\Users\AYOO\Desktop\EDUCARE
start "MuchiPondo Maths Server" /min cmd /k "call venv\Scripts\activate.bat && python app.py"
timeout /t 4 /nobreak >nul
start "" http://127.0.0.1:5000
exit
