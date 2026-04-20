# Fullstack Agent Challenge

This is a small local full-stack app built with a FastAPI backend and a React frontend.

The user enters a task, the backend validates it, analyzes intent, routes it to the appropriate tool when it is a supported single-intent request, stores the result, and shows the full trace in the UI.


## Project Structure

```text
fullstack-agent-challenge/
  README.md
  backend/
    app/
      __init__.py
      api.py
      main.py
      agent/
        __init__.py
        audit_logger.py
        controller.py
        tool_definitions.py
      db/
        __init__.py
        tasks.py
        session.py
      tools/
        __init__.py
        calculator.py
        text_processor.py
        weather_mock.py
    requirements.txt
    tasks.db
  frontend/
    index.html
    package-lock.json
    package.json
    vite.config.js
    src/
      App.jsx
      api.js
      main.jsx
      styles.css
      components/
        HistoryPanel.jsx
        ResultPanel.jsx
        TaskForm.jsx
```

## Backend Setup

Note: Requires Python 3.13.x. Python 3.14 is not supported by the current dependency set.

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend should come up on `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173`.

## How It Works

- `POST /tasks` takes the task text, sends it through the controller, stores either the successful result or the rejected request trace, and returns the saved record when the task is accepted.
- `GET /tasks` returns task history.
- `GET /tasks/{id}` returns one task with the full execution trace.

The routing is rule-based and lightweight.

- Tools are listed in the controller through a small registry class.
- Each tool carries its own scoring logic, so the controller can ask every tool for intent evidence without embedding tool-specific matching rules in one place.
- The controller flow is: validate task > analyze intent > resolve route > execute or reject.
- Tool scores are used as routing evidence, not as the routing policy by themselves.
- If the request contains multiple supported intents, the controller rejects it and asks the user to split it into separate requests.
- If no tool reaches the confidence threshold, the controller rejects the task and asks the user to clarify it.

Right now there are 3 tools:

- `weather_mock`
- `calculator`
- `text_processor`



## Current Limitations

- Weather is mock data with static predefined city lists
- The system supports only one tool per request
- Multi-intent requests are rejected, multiple tool runs not supported
- Routing is rule-based and depends on keyword and pattern matching

## Tested Inputs and Outputs

The following inputs were run against the current backend controller and produced these outputs:

```text
Input: uppercase hello world
Selected tool: text_processor
Output: HELLO WORLD

Input: word count this sentence has five words
Selected tool: text_processor
Output: Word count: 5

Input: calculate 5 * 8
Selected tool: calculator
Output: 40

Input: what is the weather in Edmonton
Selected tool: weather_mock
Output: Edmonton: 8°C, Windy

Input: calculate 2 + 2 and weather in Edmonton
Rejected: This request includes multiple intents. Please enter one intent at a time.

Input: hello there
Rejected: Intent cannot be validated with the current level of confidence. Please clarify the task.

Input: calculate 5 / 0
Rejected after tool selection: Division by zero is not supported.
```


##Walkthrough Video Link
- https://uofc-my.sharepoint.com/:v:/g/personal/kaushik_mazumder_ucalgary_ca/IQAEzO4Kd51GTrBxmUt4Mk_JAQF72pV4EWN0TTGhKT021rk?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=V9KERD
