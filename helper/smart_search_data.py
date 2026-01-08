import os
from datetime import datetime

def save_daily_record(fullName, dateOfBirth, idNumber, reference_code, status, append=False):
    folder_path = os.path.join("data", "dynamic")
    os.makedirs(folder_path, exist_ok=True)

    today_str = datetime.now().strftime("%d%m%Y")
    file_name = f"smart-search-individual-{today_str}.txt"
    file_path = os.path.join(folder_path, file_name)

    header = "Full Name,Date Of Birth,ID Number,Reference Code,Status\n"
    file_exists = os.path.exists(file_path)
    mode = "a" if append and file_exists else "w"
    with open(file_path, mode, encoding="utf-8") as f:
        if not file_exists:
            f.write(header)
        if not append:
            f.write(header)
        f.write(f"{fullName},{dateOfBirth},{idNumber},{reference_code},{status}\n")
    return file_path
