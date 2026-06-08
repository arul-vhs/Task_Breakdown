# Agent OnboardX - Production Goal Operating System

Agent OnboardX is a production-grade, multi-tenant AI-powered Goal Operating System designed to help users define goals, discover execution strategies, audit readiness, generate deterministic calendars, track checklist progress, and utilize adaptive replanning via stateful LLM feedback loops.

---

## 🚀 Key Features

* **Multi-Tenant SaaS isolation**: Scopes database operations and configurations to individual users via JSON Web Token metadata.
* **LangGraph Stateful Orchestration**: Integrates step node routing (Discovery, Intelligence, Strategy, Readiness, Planning, Task Generation, Scheduling, Execution, Coaching, Adaptive Replanning) with user checkpoints.
* **Deterministic Local Scheduling**: Sequences tasks topologically inside Python using Kahn's algorithm and maps work style time blocks locally.
* **Local Telemetry & Streaks Calculator**: Aggregates completions, health levels, and consistency logs entirely in Python services to protect against model hallucinations.
* **AI Coach Center**: Stateful chat interactions using Gemini to advice on risk mitigation.
* **Modern Glassmorphic React UI**: Designed in Next.js 15, styled with Tailwind CSS and premium Outfit/Inter typography.

---

## 📂 Project Organization

```
├── backend/
│   ├── app/
│   │   ├── api/v1/         # FastAPI Authentication & Goals controllers
│   │   ├── database/       # SQLAlchemy engine pooling & sessions
│   │   ├── langgraph/      # State definition & Node workflows
│   │   ├── models/         # SQLAlchemy DB schema models
│   │   ├── repositories/   # User & Goals database persistence functions
│   │   ├── security/       # JWT issuing & password bcrypt hashing
│   │   └── services/       # AI Orchestrator, Scheduler, Progress engines
│   └── requirements.txt    # Python packages
│
└── frontend/
    ├── src/
    │   ├── app/            # Next.js 15 routing layout
    │   ├── store/          # Zustand global store manager
    │   ├── services/       # API call interfaces
    │   └── components/     # UI widgets
    └── package.json        # Frontend node packages
```

---

## 🛠️ Local Installation & Launch

### 1. Backend API Server
Navigate to the backend folder, create a virtual environment, and install libraries:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate # Or venv/bin/activate on Mac/Linux
pip install -r requirements.txt
```

Set up your environment variables inside a `.env` file:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/agent_onboardx
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro
```

Run the FastAPI hot-reload development server:
```bash
python app/main.py
```
View backend documentation and endpoints interactive sandbox at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Next.js 15 Web Client
Navigate to the frontend folder and install node modules:
```bash
cd frontend
npm install --legacy-peer-deps
```

Start the Next.js local server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) inside your browser.

---

## 📜 Full Database Schema

```mermaid
erDiagram
    USERS ||--|| PROFILES : has
    USERS ||--o{ GOALS : creates
    USERS ||--o{ PROGRESS_LOGS : records
    GOALS ||--|| GOAL_CONTEXT : contains
    GOALS ||--o{ STRATEGIES : defines
    GOALS ||--|| READINESS_ANALYSES : evaluates
    GOALS ||--|| EXECUTION_PLANS : generates
    GOALS ||--o{ TASKS : decomposes
    GOALS ||--|| SCHEDULES : schedules
    GOALS ||--o{ SCHEDULE_VERSIONS : tracks
    GOALS ||--o{ REFLECTIONS : journals
    GOALS ||--|| COACH_INSIGHTS : monitors
    GOALS ||--o{ REPLANNING_HISTORY : logs
```

The database structures utilize PostgreSQL constraints, UUID keys, and explicit scoping query hooks for multi-tenant data safety.
