import json
import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tasks.json")

def generate_plan():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    tasks = data["tasks"]

    # Start schedule at 9 AM
    start_time = datetime.strptime("09:00", "%H:%M")
    plan = []

    for task in tasks:
        duration = task["duration"]
        end_time = start_time + timedelta(hours=duration)

        plan.append({
            "task": task["title"],
            "start": start_time.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M")
        })

        start_time = end_time  # Update pointer

    return plan
