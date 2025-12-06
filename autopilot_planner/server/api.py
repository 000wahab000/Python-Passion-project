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

@api.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = load_tasks()
    return jsonify({"tasks": tasks})

@api.route('/tasks', methods=['POST'])
def add_task():
    req_data = request.get_json()
    title = req_data.get('title')
    duration = req_data.get('duration')
    if not title or not isinstance(duration, (int, float)):
        return jsonify({"error": "Invalid title or duration"}), 400

    tasks = load_tasks()
    tasks.append({"title": title, "duration": duration})
    save_tasks(tasks)
    return jsonify({"status": "ok"})

@api.route('/tasks/<int:index>', methods=['DELETE'])
def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
        return jsonify({"status": "deleted"})
    return jsonify({"error": "Invalid index"}), 400

@api.route('/plan', methods=['GET'])
def get_plan():
    from autopilot_planner.agents.planner import generate_plan
    plan = generate_plan()
    return jsonify({"plan": plan})

@api.route('/ai/suggestions', methods=['POST'])
def ai_suggestions():
    req_data = request.get_json()
    tasks = req_data.get('tasks', [])
    from autopilot_planner.agents.ai_agent import ai_generate_task_suggestions
    suggestions = ai_generate_task_suggestions(tasks)
    return jsonify({"suggestions": suggestions})

@api.route('/ai/chat', methods=['POST'])
def ai_chat():
    req_data = request.get_json()
    message = req_data.get('message', '')
    tasks = req_data.get('tasks', [])
    from autopilot_planner.agents.ai_agent import ai_chat
    reply = ai_chat(message, tasks)
    return jsonify({"reply": reply})
