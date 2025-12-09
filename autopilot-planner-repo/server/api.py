from flask import Blueprint, request, jsonify
import json
import os

api = Blueprint('api', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tasks.json")

def load_tasks():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data["tasks"]

def save_tasks(tasks):
    with open(DATA_PATH, "w") as f:
        json.dump({"tasks": tasks}, f, indent=4)

def read_tasks():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data

def write_tasks(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

@api.route('/api/tasks', methods=['GET'])
def get_tasks():
    data = read_tasks()
    data["tasks"].sort(key=lambda x: x["due"] or "9999-12-31")
    return jsonify(data)

@api.route('/api/tasks', methods=['POST'])
def add_task():
    req_data = request.get_json()
    task = req_data.get('title')
    if not task:
        return jsonify({"error": "Invalid task"}), 400

    data = read_tasks()
    data["tasks"].append({
        "text": task,
        "status": "todo",
        "category": "general",
        "due": None
    })
    write_tasks(data)
    return jsonify({"status": "ok"})

@api.route('/api/tasks/<int:index>', methods=['DELETE'])
def delete_task(index):
    data = read_tasks()
    tasks = data.get('tasks', [])
    if index < 0 or index >= len(tasks):
        return jsonify({'error': 'index out of range'}), 400
    tasks.pop(index)
    data['tasks'] = tasks
    write_tasks(data)
    return jsonify({'status':'deleted'})

@api.route('/api/tasks/<int:index>', methods=['PATCH'])
def update_task(index):
    data = read_tasks()
    if index < 0 or index >= len(data["tasks"]):
        return jsonify({"error": "Index out of range"}), 400

    new_text = request.json.get("text", "").strip()
    if not new_text:
        return jsonify({"error": "No task content"}), 400

    data["tasks"][index]["text"] = new_text
    write_tasks(data)
    return jsonify({"tasks": data["tasks"]})

@api.route("/api/tasks/<int:index>/status", methods=["PATCH"])
def update_status(index):
    data = read_tasks()
    if index < 0 or index >= len(data["tasks"]):
        return jsonify({"error": "Index out of range"}), 400

    new_status = request.json.get("status", "").strip()
    if new_status not in ["todo", "in-progress", "done"]:
        return jsonify({"error": "Invalid status"}), 400

    data["tasks"][index]["status"] = new_status
    write_tasks(data)
    return jsonify({"tasks": data["tasks"]})

@app.route("/api/tasks/<int:index>/category", methods=["PATCH"])
def update_category(index):
    data = read_tasks()
    if index < 0 or index >= len(data["tasks"]):
        return jsonify({"error": "Index out of range"}), 400

    new_category = request.json.get("category", "").strip()
    if not new_category:
        return jsonify({"error": "Invalid category"}), 400

    data["tasks"][index]["category"] = new_category
    write_tasks(data)
    return jsonify({"tasks": data["tasks"]})

@app.route("/api/tasks/<int:index>/due", methods=["PATCH"])
def update_due(index):
    data = read_tasks()
    if index < 0 or index >= len(data["tasks"]):
        return jsonify({"error": "Index out of range"}), 400

    new_due = request.json.get("due", None)
    # Accept empty or ISO-format date string
    if new_due is not None and not isinstance(new_due, str):
        return jsonify({"error": "Invalid date"}), 400

    data["tasks"][index]["due"] = new_due
    write_tasks(data)
    return jsonify({"tasks": data["tasks"]})

@api.route('/api/plan', methods=['GET'])
def get_plan():
    from agents.planner import generate_plan
    plan = generate_plan()
    return jsonify({"plan": plan})

@api.route('/api/ai/suggestions', methods=['POST'])
def ai_suggestions():
    req_data = request.get_json()
    tasks = req_data.get('tasks', [])
    from agents.ai_agent import ai_generate_task_suggestions
    suggestions = ai_generate_task_suggestions(tasks)
    return jsonify({"suggestions": suggestions})

@api.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    req_data = request.get_json()
    message = req_data.get('message', '')
    tasks = req_data.get('tasks', [])
    from agents.ai_agent import ai_chat
    reply = ai_chat(message, tasks)
    return jsonify({"reply": reply})

@api.route('/api/calendar/events', methods=['GET'])
def get_calendar_events():
    # Placeholder for calendar events
    # In future, generate from tasks with dates
    events = [
        {
            "title": "Sample Task",
            "start": "2025-12-08T10:00:00",
            "end": "2025-12-08T11:00:00"
        }
    ]
    return jsonify(events)

@api.route('/api/ai/prioritize', methods=['POST'])
def ai_prioritize():
    req_data = request.get_json()
    tasks = req_data.get('tasks', [])
    from agents.ai_agent import ai_prioritize_tasks
    prioritized = ai_prioritize_tasks(tasks)
    return jsonify({"prioritized": prioritized})
