from autopilot_planner.agents.planner import generate_plan

print("generate_plan.py is running...")

plan = generate_plan()

print("\nToday's Plan:\n")
for item in plan:
    print(f"{item['start']} - {item['end']}: {item['task']}")

