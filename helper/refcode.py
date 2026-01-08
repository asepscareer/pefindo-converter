import json
from datetime import datetime
from pathlib import Path

def generate_reference_code(storage_path="data/dynamic/refcode.json"):
    today = datetime.now().strftime("%Y%m%d")
    storage = Path(storage_path)

    if not storage.exists():
        data = {"date": today, "refcode": 0}
    else:
        data = json.loads(storage.read_text())

    if data.get("date") != today:
        data["date"] = today
        data["refcode"] = 0

    data["refcode"] += 1
    next_num = data["refcode"]
    
    storage.write_text(json.dumps(data))
    return f"HNBK{today}{next_num:04d}"
