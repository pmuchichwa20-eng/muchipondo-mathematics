
import os
import sys
import time
import shutil
import threading
import webbrowser
from pathlib import Path

# Locate the application files
if getattr(sys, "frozen", False):
    app_folder = Path(sys._MEIPASS)
else:
    app_folder = Path(__file__).resolve().parent

# Create a permanent database folder
data_folder = Path(os.environ["LOCALAPPDATA"]) / "MuchiPondo Maths"
data_folder.mkdir(parents=True, exist_ok=True)

database = data_folder / "educare.db"
original_database = app_folder / "educare.db"

# Copy the original database only on first installation
if not database.exists():
    shutil.copy2(original_database, database)

# Make all relative database connections use the permanent folder
os.chdir(data_folder)

from app import app

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")

threading.Thread(target=open_browser, daemon=True).start()

app.run(
    host="127.0.0.1",
    port=5000,
    debug=False,
    use_reloader=False
)
