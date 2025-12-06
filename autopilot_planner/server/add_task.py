import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tasks.json")

def add_task(title, duration):
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    data["tasks"].append({
        "title": title,
        "duration": duration
    })

    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)
