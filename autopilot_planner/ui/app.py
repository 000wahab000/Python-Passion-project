from flask import Flask, render_template, request
from autopilot_planner.server.add_task import add_task
from autopilot_planner.agents.planner import generate_plan

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        duration = int(request.form["duration"])
        add_task(title, duration)
        return "Task added!"
    return render_template("add.html")

@app.route("/plan")
def plan():
    plan = generate_plan()
    return render_template("plan.html", plan=plan)

if __name__ == "__main__":
    app.run(debug=True)
