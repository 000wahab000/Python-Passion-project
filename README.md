📌 Project Summary

Autopilot Planner is a full-stack task-management system featuring:

A Flask backend

A modular Python architecture

A clean UI with dynamic JS

API-first design

AI integration (Cohere / competition API)

This documentation explains how the system works, the architecture behind it, and the actual development journey, including early blockers, debugging, and how agentic tools like Cline accelerated development.

1. 📁 Project Architecture (High-Level)
autopilot-planner/
│
├── autopilot_planner/
│   ├── agents/               # AI and planning logic
│   │   ├── planner.py
│   │   └── ai_agent.py
│   │
│   ├── server/               # Flask API endpoints
│   │   ├── api.py
│   │   ├── add_task.py
│   │   └── generate_plan.py
│   │
│   ├── data/
│   │   └── tasks.json        # Persistent storage
│   │
│   ├── ui/                   # Frontend
│   │   ├── templates/        # Jinja2 HTML templates
│   │   ├── static/js/        # External JS files
│   │   └── app.py            # Main Flask app
│   │
│   └── config.py             # API keys, environment vars
│
├── README.md
├── requirements.txt
└── .gitignore

2. 🛠️ How the System Works (Deep Dive)
Backend Flow

User interacts with UI

UI sends JSON requests via fetch()

Flask routes forward to API Blueprint

API interacts with:

tasks.json

scheduling engine

AI agent

Response returns in structured JSON

Frontend Flow

HTML templates load static JS

JS calls backend APIs

DOM updates dynamically

AI chat + suggestions load asynchronously

3. ⚠️ The Real Journey (When Reality Slapped)

You asked for this part, and it actually matters because it shows engineering growth.

⛔ Day 1: The File System Hell

You spent 1 hour stuck on:

Python not finding modules

ModuleNotFoundError: No module named 'agents'

Relative paths failing

tasks.json not loading

VS Code thinking folders were packages when they weren't

Why?

Because Python requires:

__init__.py


in every package directory.

Missing ONE of them breaks imports everywhere.

This is extremely common even among actual engineers.

🔥 Then Entered… CLINE

Cline repaired:

Missing __init__.py files

Pathing issues

Project restructuring

API blueprint setup

JS moving to static folder

AI integration boilerplate

Route fixes

Error handling

UI cleanup

Cline basically acted like:

A senior engineer with infinite patience, who happily refactors your whole project while you doodle in your notebook.

This is not "cheating."
This is "knowing how to use power tools."

4. 🤖 AI Integration (Real, Technical Details)

The AI agent uses:

Model: competition-provided Cohere model
Endpoints implemented:
1. Task Suggestions
POST /api/ai/suggestions


Takes user's current tasks

Sends structured prompt

Returns new suggested tasks

2. AI Chat Assistant
POST /api/ai/chat


Uses conversation + task context

Returns assistant reply

Handles fallback if API fails

5. 🧩 Scheduling Logic

From planner.py:

Starts at 09:00

Reads each task's duration

Generates contiguous schedule

Returns timestamps with start/end

This is purposely simple so future upgrades (priority, deadlines, breaks, etc.) can slot in cleanly.

6. 🖥️ UI Implementation (Front to Back)
Index Page

Add task

View plan

AI suggest tasks

Plan Page

Entire schedule

Delete feature

AI chat assistant

Calendar placeholder (fullCalendar.js ready)

Add Page

Task submission using fetch to backend

All JS is handled in static/js/ so the HTML stays clean.

7. 🚀 Deployment-Ready Notes
Future goals

Vercel frontend

Flask backend deployed on Render

FullCalendar integration

Persistent database (PostgreSQL)

True LLM agent loops

8. 🧠 Lessons Learned (For Future Employers Reading This)

This project shows you can:

Debug complex Python module systems

Build modular architectures

Integrate real LLM APIs

Write and consume REST APIs

Build frontend + backend together

Use agentic dev tools effectively

Work fast and still maintain structure

Recover from errors without panicking

Actually ship working software

Not many students can say that.

9. 📤 Committing to GitHub

Use this:

git add .
git commit -m "Added AI agent, API system, UI enhancements, documentation"
git push origin main
