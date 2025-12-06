# Autopilot Planner

A modern web-based task planning application that helps users organize their daily tasks and generate optimized schedules. Built with Flask and featuring a responsive UI powered by TailwindCSS, Autopilot Planner provides an intuitive interface for adding tasks and viewing generated plans.

![Autopilot Planner Screenshot](https://via.placeholder.com/800x400?text=Screenshot+Coming+Soon)

## Features

- **Task Management**: Easily add tasks with titles and estimated durations
- **Schedule Generation**: Automatically create daily plans starting from 9 AM
- **Modern UI**: Clean, responsive interface built with TailwindCSS
- **Real-time Planning**: Instant schedule updates as tasks are added
- **Professional Design**: Card-based layouts and intuitive navigation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/000wahab000/Python-Passion-project.git
   cd Python-Passion-project
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask
   ```

3. **Navigate to the project directory**
   ```bash
   cd autopilot_planner
   ```

## Running the Application

### Start the Flask Backend

```bash
python -m ui.app
```

The application will start on `http://127.0.0.1:5000/`

### Access the Web Interface

Open your browser and navigate to:
- **Home**: http://127.0.0.1:5000/
- **Add Task**: http://127.0.0.1:5000/add
- **View Plan**: http://127.0.0.1:5000/plan

## Project Structure

```
autopilot_planner/
├── __init__.py
├── agents/
│   ├── __init__.py
│   └── planner.py          # Core planning logic
├── data/
│   ├── __init__.py
│   └── tasks.json          # Task storage
├── server/
│   ├── __init__.py
│   ├── add_task.py         # Task addition functionality
│   └── generate_plan.py    # Plan generation utilities
├── ui/
│   ├── __init__.py
│   ├── app.py              # Flask application
│   └── templates/
│       ├── index.html      # Home page
│       ├── add.html        # Add task page
│       └── plan.html       # View plan page
└── workflows/
    └── daily_plan.yaml     # Kestra workflow configuration
```

## Usage

1. **Add Tasks**: Use the "Add Task" page to input task titles and durations in hours
2. **View Plan**: Navigate to "View Plan" to see your automatically generated daily schedule
3. **Schedule Logic**: Tasks are scheduled sequentially starting from 9:00 AM based on their durations

## API Endpoints

- `GET /` - Home page
- `GET/POST /add` - Add task form and processing
- `GET /plan` - Display generated plan

## Future Roadmap

### Phase 1: Enhanced AI Integration
- [ ] Integrate Oumi agent for intelligent task scheduling
- [ ] Add natural language task creation via AI parsing
- [ ] Implement smart scheduling suggestions based on task analysis

### Phase 2: Workflow Automation
- [ ] Deploy Kestra workflow for daily automated plan generation
- [ ] Add email notifications for daily plans
- [ ] Implement recurring task templates

### Phase 3: Deployment & Scaling
- [ ] Separate frontend (Next.js/Vue.js) deployed on Vercel
- [ ] RESTful API backend with proper CORS handling
- [ ] Database integration (PostgreSQL/MongoDB) for multi-user support
- [ ] User authentication and personal dashboards

### Phase 4: Advanced Features
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Priority-based task ordering
- [ ] Time blocking and focus session suggestions
- [ ] Progress tracking and completion analytics

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, TailwindCSS
- **Data Storage**: JSON files (upgrade planned to database)
- **Deployment**: Flask development server (production WSGI planned)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Wahab**
- Passionate about building productivity tools and AI-assisted applications
- Focus on clean code, user experience, and scalable architectures

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Note: This project is currently in active development. Features marked in the roadmap are planned for future releases.*
