from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import os

FOLDER = "data/dynamic"


def clean_old_files():
    today = datetime.today()
    limit = today - timedelta(days=14)

    for filename in os.listdir(FOLDER):
        date_str = filename[-8:]

        try:
            file_date = datetime.strptime(date_str, "%d%m%Y")
        except ValueError:
            continue

        if file_date < limit:
            file_path = os.path.join(FOLDER, filename)
            try:
                os.remove(file_path)
                print(f"[CLEANER] Removed: {filename}")
            except Exception as e:
                print(f"[CLEANER] Failed deleting {filename}: {e}")
