from flask import Flask, render_template
from flask_cors import CORS
from autopilot_planner.server.api import api

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for all routes

# Register the API blueprint
app.register_blueprint(api, url_prefix='/api')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/plan")
def plan():
    return render_template("plan.html")

if __name__ == "__main__":
    app.run(debug=True)
