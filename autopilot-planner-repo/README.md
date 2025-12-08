# Autopilot Planner

Autopilot Planner is a modular, extensible task-scheduling application built with Python, Flask, and a clean API-first architecture.
It helps users:

- Add tasks
- Generate a daily schedule
- Receive AI-powered task suggestions
- Chat with a built-in AI assistant
- Prepare for future integrations (calendar sync, workflows, LLM scheduling)

## ⭐ Features

### ✔ Task Management
- Add tasks with title + duration
- View ordered daily plan
- Delete tasks by index

### ✔ AI-Powered Features
- Smart AI task suggestions using a real LLM API
- Chat-based AI assistant on the Planning page
- Modular AI layer for future models or prompts

### ✔ API-First Backend
Every feature is exposed through clean JSON endpoints:

- GET  `/api/tasks`
- POST `/api/tasks`
- DELETE `/api/tasks/<index>`
- GET  `/api/plan`
- POST `/api/ai/suggestions`
- POST `/api/ai/chat`

### ✔ Clean & Responsive UI
Built with TailwindCSS + organized JS modules
- Home screen
- Add Task page
- Plan page with split layout (Schedule + AI Assistant)

## 📁 Project Structure

```
autopilot-planner-repo/
├── __init__.py
├── .gitignore
├── config.py
├── README.md
├── requirements.txt
├── agents/
│   ├── __init__.py
│   ├── ai_agent.py
│   └── planner.py
├── autopilot_planner/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   └── planner.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── tasks.json
│   ├── server/
│   │   ├── __init__.py
│   │   ├── add_task.py
│   │   └── generate_plan.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── templates/
│   │   │   ├── add.html
│   │   │   ├── index.html
│   │   │   └── plan.html
│   │   └── workflows/
│   │       └── __init__.py
│   └── workflows/
│       └── __init__.py
├── data/
│   ├── __init__.py
│   └── tasks.json
├── server/
│   ├── __init__.py
│   ├── add_task.py
│   ├── api.py
│   └── generate_plan.py
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── static/
│   │   └── js/
│   │       ├── add.js
│   │       ├── index.js
│   │       └── plan.js
│   ├── templates/
│   │   ├── add.html
│   │   ├── index.html
│   │   └── plan.html
│   └── workflows/
│       └── __init__.py
└── workflows/
    └── __init__.py
```

## 🚀 How to Run

```bash
pip install -r requirements.txt
py -m autopilot_planner.ui.app
