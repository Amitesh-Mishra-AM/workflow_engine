# Mini Workflow / Graph Engine (AI Engineering Assignment)

This project is a **minimal workflow engine** built with **Python + FastAPI**.

It lets you define a simple **graph of nodes (steps)**, pass a **shared state** between them, and execute the graph via APIs. It also demonstrates a sample **Code Review Mini-Agent** workflow as required in the assignment brief.

---

## 🌐 High-Level Overview

Core ideas:

- A **graph** is defined using:
  - **Nodes** → Python functions that read & modify a shared `state`
  - **Edges** → mapping that decides which node runs after which
  - **Start node** → entry point for execution
- A **shared state dictionary** flows through nodes and is mutated step-by-step.
- The engine supports:
  - Sequential execution
  - Simple branching
  - Simple looping

The project is intentionally **small and focused** to show clarity of:
- State → transitions → loops
- API design
- Code structure

---

## 🧱 Features

### 1. Workflow / Graph Engine

- Define a graph as:
  - `nodes: List[str]`
  - `edges: Dict[str, str]` (e.g. `"extract_functions" -> "check_complexity"`)
  - `start_node: str`
- Each **node** is a Python function registered in a central **node registry**.
- Shared `state: Dict[str, Any]` flows through all nodes.

### 2. Branching & Looping

- Regular nodes return:  
  `state: Dict[str, Any>`
- Special nodes can return:  
  `(state, next_node_name)`  
  This allows:
  - Conditional routing
  - Simple loops (rerun a node until a condition is satisfied)

Example: `evaluate_quality` node:
- If `quality_score < threshold` and `loop_count < max_loops`  
  → loop back to `"suggest_improvements"`  
- Else  
  → go to `"finish"`

### 3. Tool / Node Registry

- All available node functions are registered in `NODE_REGISTRY` (a simple dictionary).
- Graphs reference nodes **by name**.
- This keeps the system **extensible** and easy to reason about.

### 4. FastAPI Endpoints

- `POST /graph/create`  
  Create a graph (nodes + edges) and get a `graph_id`.

- `POST /graph/run`  
  Run a graph with an initial state and get:
  - `run_id`
  - `final_state`
  - execution `log` (ordered list of executed nodes)
  - `status` and optional `error`

- `GET /graph/state/{run_id}`  
  Fetch the state and log of a previously executed run.

> Storage is in-memory for simplicity.
## ⚡ Async Execution & Real-Time Streaming
### Async Graph Execution

The engine supports async execution for long-running workflows.

- Endpoint: `POST /graph/run_async`
- Internally uses `asyncio.to_thread` to offload graph execution to a worker thread.
- This prevents blocking the FastAPI event loop when nodes perform expensive operations
  (e.g., simulated delays using `time.sleep`).

This design allows the system to remain responsive even for long-running agent workflows.

### WebSocket: Real-Time Workflow Streaming

A WebSocket endpoint is provided to stream workflow execution step-by-step.

- Endpoint: `ws://127.0.0.1:8000/ws/graph/run`

#### How it works:
1. Client sends:
   ```json
   {
     "graph_id": "<graph_id>",
     "initial_state": { ... }
   }
    ```
2. Server streams events in real-time:
    - before_node
    - after_node
    - completed
    - error (if any)
Example streamed message:
```json
{
  "event": "after_node",
  "node": "detect_issues",
  "state": {
    "issue_count": 2,
    "quality_score": 70
  }
}
```
This enables:
- Live visualization of agent execution

- Debugging workflows step-by-step

- Building interactive UIs on top of the engine

✅ This shows:
- Systems thinking
- Real-time design awareness
- Production-level mindset
## 🧪 Sample Workflow: Code Review Mini-Agent (Option A)

The example workflow implements a **simple, rule-based code review agent**:

Nodes:

1. `extract_functions`  
   - Extracts function names from the input code.

2. `check_complexity`  
   - Approximates a **complexity score** based on:
     - number of lines
     - number of functions

3. `detect_issues`  
   - Counts basic “issues”:
     - long lines (`> 80` characters)
     - presence of `"TODO"`
     - usage of `print()` calls

4. `suggest_improvements`  
   - Generates textual suggestions.
   - Computes a numeric `quality_score` in `[0, 100]` based on:
     - complexity
     - number of issues
     - loop count (each loop slightly improves quality)

5. `evaluate_quality`  
   - Implements **branching + looping**:
     - if `quality_score < threshold` and `loop_count < max_loops`  
       → go back to `suggest_improvements`
     - else  
       → go to `finish`

6. `finish`  
   - Final node – returns state as-is.

##  🔀 Graph Edges

```json
{
  "extract_functions": "check_complexity",
  "check_complexity": "detect_issues",
  "detect_issues": "suggest_improvements",
  "suggest_improvements": "evaluate_quality"
}
```
---
## 📁 Project Structure: 

```bash
app/
├── __init__.py
├── main.py                # FastAPI app & endpoints
├── models.py              # Pydantic models & enums
├── engine.py              # Graph engine & in-memory storage
├── registries.py          # Node registry (tool registry)
└── workflows_code_review.py  # Code Review Mini-Agent nodes
```

## ⚙️ Requirements

- Python 3.12 (tested on 3.12.4)
- pip

Install dependencies:
```bash
pip install fastapi uvicorn "pydantic>=2.0"
```
## 📡 API Usage
1. Create a Graph

    Endpoint
    ```bash
    POST /graph/create
    Content-Type: application/json
    ```

    Request body
    ```json
    {
    "nodes": [
        "extract_functions",
        "check_complexity",
        "detect_issues",
        "suggest_improvements",
        "evaluate_quality",
        "finish"
    ],
    "edges": {
        "extract_functions": "check_complexity",
        "check_complexity": "detect_issues",
        "detect_issues": "suggest_improvements",
        "suggest_improvements": "evaluate_quality"
    },
    "start_node": "extract_functions"
    }
    ```
    Response
    ```json

    {
    "graph_id": "f7f6f2c4-2d85-4f7d-9a8f-3a5a0d7b1e88"
    }
    ```
2. Run a Graph

    Endpoint
    ```http
    POST /graph/run
    Content-Type: application/json
    ```
    Request body
    ```json
    {
    "graph_id": "f7f6f2c4-2d85-4f7d-9a8f-3a5a0d7b1e88",
    "initial_state": {
        "code": "def foo(x):\n    print(x)\n    # TODO: improve this\n",
        "threshold": 75,
        "max_loops": 3
    }
    }
    ```

    Response (example)
    ```json
    {
    "run_id": "93a3f79e-35b1-4bcf-a654-b5e3bb0a0f9a",
    "final_state": {
        "code": "def foo(x):\n    print(x)\n    # TODO: improve this\n",
        "lines": [
        "def foo(x):",
        "    print(x)",
        "    # TODO: improve this"
        ],
        "functions": [
        "foo"
        ],
        "complexity_score": 18,
        "issue_count": 2,
        "suggestions": [
        "Reduce function sizes or split logic into smaller helpers.",
        "Fix code smells such as long lines, TODOs, and print statements."
        ],
        "quality_score": 80,
        "threshold": 75,
        "loop_count": 2,
        "max_loops": 3
    },
    "log": [
        "extract_functions",
        "check_complexity",
        "detect_issues",
        "suggest_improvements",
        "evaluate_quality",
        "suggest_improvements",
        "evaluate_quality",
        "finish"
    ],
    "status": "completed",
    "error": null
    }
    ```

    This shows:

    - How the state was enriched step-by-step.

    - How looping between suggest_improvements and evaluate_quality works.

    - Which nodes executed in which order (via log).

3. Get Run State

    Endpoint

    ```http
    GET /graph/state/{run_id}   
    ```
    Response (example)
    ```json
    {
    "run_id": "93a3f79e-35b1-4bcf-a654-b5e3bb0a0f9a",
    "state": { ... },
    "log": [ ... ],
    "status": "completed",
    "error": null
    }
    ```

    In this implementation, runs are executed synchronously and finish quickly, so the state is final. The same mechanism can be extended to long-running / async runs.

## 🚀 How to Run the Project
1. Clone the repository
   ```bash
   git clone <your-repo-url>
   cd workflow_engine
   ```
2. Install dependencies
    ```bash
    pip install fastapi uvicorn "pydantic>=2.0"
    ```
3. Start the server
    ```bash
    uvicorn app.main:app --reload
    ```
4. Open API docs
    - postman http://127.0.0.1:8000/docs

## 🧠 Design Choices

Simple over complex:
Focused on clarity of the engine logic instead of building a full-blown framework.

In-memory storage:
Graphs and runs are stored in dictionaries (GraphEngine.graphs and GraphEngine.runs) to keep the implementation small and easy to read.

Node registry pattern:
Decouples graph definition from node implementation.

Branching via return type:
A node can control routing by returning (state, next_node_name) instead of just state.

## 🚧 Possible Improvements (with more time)

If I had more time, I would extend the engine with:

1. Persistent storage

    - Use SQLite or Postgres to store graphs and run histories.

    - Add created_at / updated_at timestamps for runs.

2. Richer graph model

    - Support multiple outgoing edges per node (based on named conditions).

    - Visual representation of graphs (export to JSON/Graphviz).

3. Async execution

    - Offload long-running graphs to background tasks.

    - Provide an async runner (run_graph_async) that doesn’t block the FastAPI event loop.

4. WebSocket streaming

    - Add a WebSocket endpoint that streams node execution logs and intermediate states in real-time as the workflow runs.

5. Validation & tooling

    - Static validation of graph definitions (e.g., unreachable nodes, cycles).

    - Better typing for state (Pydantic models per workflow).

## 🏗️ Why This Design?

The goal of this project was not to recreate a full framework like LangGraph,
but to demonstrate:

- Clear state-driven execution
- Simple, inspectable control flow
- Extensibility through registries
- Practical API design

The system favors readability and correctness over abstraction-heavy designs,
making it easy to extend with new nodes, workflows, and execution strategies.


## ✅ Summary

This project implements a minimal but complete workflow engine with:

   - Graph definition via API
   - Node registry
   - Shared state propagation
   - Branching + looping
   - FastAPI-based interface