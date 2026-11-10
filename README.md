# StratagemAI - Autonomous AI Planner & Goal Decomposition Engine

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-green.svg)](https://langchain.com)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-E92063.svg?logo=pydantic&logoColor=white)](https://pydantic.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**StratagemAI** is a goal-oriented planning engine implementing the **Plan-and-Solve** and **Hierarchical Planning** paradigm in Python. Rather than single-turn generation or uncoordinated tool calling, StratagemAI decomposes complex, ambiguous goals into topologically sorted milestones, coordinates execution across specialized agent personas, and dynamically re-plans when faced with environment shifts or failure states.

---

## Strategic Workflow

```mermaid
graph TD
    Goal([High-Level Objective]) --> Planner[StratagemAI Planner Engine]
    Planner --> |Structured JSON Output| Plan[Hierarchical Directed Plan]
    
    subgraph Execution Loop
        Plan --> Task1[Milestone 1: Architecture]
        Task1 --> |Output Context| Task2[Milestone 2: Processing]
        Task2 --> |Output Context| Task3[Milestone 3: Deployment]
        
        Task2 -.-> |Failure / New Constraint| Replan[Dynamic Replanner]
        Replan --> |Re-index & Insert Milestones| Plan
    end
    
    Task3 --> Dossier[Executive Strategic Dossier]
    Dossier --> UI[Streamlit Interactive Dashboard]
```

---

## Core Capabilities

- **Hierarchical Goal Decomposition:** Breaks ambiguous requests into discrete, dependency-mapped milestones with assigned personas (e.g. Lead Architect, Data Engineer, QA Lead).
- **Dependency-Aware Execution:** Enforces prerequisite rules—subtasks will not execute unless prerequisite parent tasks have completed.
- **Context Synthesis Across Steps:** Each step's output is injected into the prompt context for subsequent milestones, maintaining deep continuity.
- **Dynamic Replanning Engine:** Handles runtime exceptions or shifting scope by modifying remaining tasks and logging an audit trail of changes.
- **Dossier & Schema Export:** Instant download of the full plan in Markdown or Pydantic JSON.
- **Zero-Key Demo Blueprints:** Out-of-the-box support for pre-baked enterprise pipelines.

---

## Quick Start

### 1. Installation
```bash
git clone https://github.com/<your-username>/StratagemAI.git
cd StratagemAI
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Launch Application
```bash
streamlit run app.py
```

---

## Comprehensive Documentation
For formal state machine definitions, algorithmic breakdowns, and benchmark traces, refer to [Project Documentation](docs/Project_Documentation.md).

---

## License
MIT License. Open for educational and commercial development.
