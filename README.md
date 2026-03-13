# 🧭 Multi-Agent Travel Planner (LangGraph + FastAPI)

A multi-agent AI travel planning system built using LangGraph, LangChain, Groq LLM, and FastAPI.

The system uses a Supervisor Agent architecture where a central agent dynamically decides which specialized agent should run next.

Agents collaborate to generate a complete travel plan including flights, hotels, activities, and budget analysis.

---

# 🚀 Features

- Multi-agent orchestration using LangGraph
- Supervisor-based dynamic agent routing
- Flight search agent
- Hotel recommendation agent
- Tourist activity agent
- Budget calculation agent
- FastAPI backend with REST endpoint
- Web search via Tavily
- Structured LLM outputs using Pydantic schemas

---

# 🏗️ System Architecture

```mermaid
flowchart TD

    A[User Request] --> B[FastAPI Endpoint]

    B --> C[LangGraph Workflow]

    C --> D[Supervisor Agent]

    D -->|Route| E[Flights Agent]
    D -->|Route| F[Hotels Agent]
    D -->|Route| G[Activities Agent]
    D -->|Route| H[Budget Analyst]

    E --> D
    F --> D
    G --> D
    H --> D

    D -->|FINISH| I[Return Travel Plan]
````

---

# 🧠 Agent Responsibilities

| Agent                | Responsibility                      |
| -------------------- | ----------------------------------- |
| **Supervisor Agent** | Decides which agent should run next |
| **Flights Agent**    | Finds flights between cities        |
| **Hotels Agent**     | Recommends hotels in destination    |
| **Activities Agent** | Suggests tourist attractions        |
| **Budget Analyst**   | Calculates total travel cost        |

---

# 📂 Project Structure

```
travel_planner
│
├── app
│   ├── agents
│   │   ├── flight_agent.py
│   │   ├── hotel_agent.py
│   │   ├── activity_agent.py
│   │   └── budget_agent.py
│   │
│   ├── config
│   │   └── settings.py
│   │
│   ├── graph
│   │   ├── state.py
│   │   ├── supervisor.py
│   │   ├── nodes.py
│   │   └── builder.py
│   │
│   ├── schemas
│   │   ├── trip_schema.py
│   │   ├── router_schema.py
│   │   └── cost_schema.py
│   │
│   ├── tools
│   │   ├── web_search.py
│   │   └── budget_tool.py
│   │
│   └── main.py
│
├── .env
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/ankita383/Trip_Planner.git
cd travel-planner
```

---

### 2️⃣ Install Dependencies using **uv**

```bash
uv sync
```

---

### 3️⃣ Set Environment Variables

Create `.env` file:

```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

---

### 4️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# 📡 API Endpoint

### Generate Travel Plan

**POST**

```
/generate-plan
```

### Example Request

```json
{
  "user_query": "Plan a trip from Delhi to Goa"
}
```

---

# 📤 Example Response

```json
{
 "status": "complete",
 "plan": [
   {
     "agent": "FlightAgent",
     "message": "Flights from Delhi to Goa..."
   },
   {
     "agent": "HotelAgent",
     "message": "Top hotels in Goa..."
   },
   {
     "agent": "ActivityAgent",
     "message": "Popular activities..."
   },
   {
     "agent": "BudgetAnalyst",
     "message": "Total cost: ₹45,000"
   }
 ]
}
```

---

# 🧩 Technologies Used

* **LangGraph** – Multi-agent workflow orchestration
* **LangChain** – Agent creation and tools
* **Groq LLM** – Fast inference
* **FastAPI** – Backend API
* **Tavily Search** – Web search tool
* **Pydantic** – Structured outputs
* **uv** – Python dependency manager

---

