import requests
from autopilot_planner.config import COMPETITION_API_KEY

def ai_generate_task_suggestions(tasks):
    """
    Given a list of tasks, call Cohere AI to generate task suggestions.
    Return a list of suggested task objects:
       [ {"title": "...", "duration": ...}, ... ]
    """
    if not COMPETITION_API_KEY or COMPETITION_API_KEY == "your-cohere-api-key-here":
        # Fallback to placeholder if no key
        if not tasks:
            return [
                {"title": "Morning exercise", "duration": 1},
                {"title": "Review emails", "duration": 0.5},
                {"title": "Plan day", "duration": 0.5}
            ]
        return []

    # Prepare prompt
    tasks_str = "\n".join([f"- {task['title']} ({task['duration']} hours)" for task in tasks])
    prompt = f"""Based on the user's current tasks:
{tasks_str}

Suggest 3-5 additional productive tasks that would complement their schedule. For each task, provide:
- Title: A clear, actionable task name
- Duration: Estimated hours (decimal allowed)

Format as JSON array of objects with "title" and "duration" fields."""

    try:
        response = requests.post(
            "https://api.cohere.ai/generate",
            headers={
                "Authorization": f"Bearer {COMPETITION_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "command-r-plus",
                "prompt": prompt,
                "max_tokens": 300,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("generations", [{}])[0].get("text", "")

        # Parse the JSON from the response
        import json
        # Extract JSON from the text (assuming it's wrapped in ```json or similar)
        start = generated_text.find('[')
        end = generated_text.rfind(']') + 1
        if start != -1 and end > start:
            json_str = generated_text[start:end]
            suggestions = json.loads(json_str)
            return suggestions
        else:
            # Fallback
            return [
                {"title": "Break time", "duration": 0.5},
                {"title": "Review progress", "duration": 0.25}
            ]
    except Exception as e:
        print(f"AI suggestion error: {e}")
        return []

def ai_chat(message, tasks):
    """
    Given a message and current tasks, call Cohere AI for chat response.
    Return a reply string.
    """
    if not COMPETITION_API_KEY or COMPETITION_API_KEY == "your-cohere-api-key-here":
        # Fallback response
        return "I'm sorry, but the AI service is not configured. Please set up your API key to enable chat functionality."

    # Prepare prompt
    tasks_str = "\n".join([f"- {task['title']} ({task['duration']} hours)" for task in tasks])
    prompt = f"""You are an AI assistant helping with task planning and productivity.

Current user's tasks:
{tasks_str}

User's message: {message}

Provide a helpful, concise response related to their tasks and productivity. Keep it under 200 words."""

    try:
        response = requests.post(
            "https://api.cohere.ai/generate",
            headers={
                "Authorization": f"Bearer {COMPETITION_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "command-r-plus",
                "prompt": prompt,
                "max_tokens": 200,
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        result = response.json()
        generated_text = result.get("generations", [{}])[0].get("text", "").strip()
        return generated_text if generated_text else "I apologize, but I couldn't generate a response at this time."
    except Exception as e:
        print(f"AI chat error: {e}")
        return "I'm sorry, there was an error processing your request. Please try again later."
