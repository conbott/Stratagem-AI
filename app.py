"""
StratagemAI - Autonomous AI Planner & Goal Decomposition Engine
Streamlit Web Application
"""

import os
import sys
import json
import time
import importlib
from pathlib import Path
import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import planner.models
import planner.engine
importlib.reload(planner.models)
importlib.reload(planner.engine)
from planner.engine import StratagemPlannerEngine
from planner.models import TaskStatus, ExecutionPlan
from planner.mock_data import PRESET_PLANS

st.set_page_config(
    page_title="StratagemAI | Strategic AI Planner",
    page_icon="map",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .planner-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #f8fafc;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
    }
    .planner-sub {
        color: #94a3b8;
        font-size: 1.0rem;
        margin-bottom: 1.5rem;
    }
    .status-badge-pending {
        background: #475569;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .status-badge-completed {
        background: #10b981;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .status-badge-failed {
        background: #ef4444;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
    .status-badge-inprogress {
        background: #f59e0b;
        color: white;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

from planner.engine import StratagemPlannerEngine
from planner.models import TaskStatus, ExecutionPlan
from planner.mock_data import PRESET_PLANS

# --- Sidebar Configuration ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/strategic-plan.png", width=64)
    st.markdown("## **StratagemAI Control**")
    st.markdown("Hierarchical Goal Planner & Dynamic Replanner.")

    st.markdown("---")
    provider = st.selectbox(
        "LLM Provider",
        options=[
            "Local Ollama (qwen2.5-coder:7b)",
            "Demo / Offline Mode (No Key Required)",
            "Gemini",
            "OpenAI",
            "Groq",
        ],
        index=0,
    )

    default_models = {
        "Local Ollama (qwen2.5-coder:7b)": "qwen2.5-coder:7b",
        "Demo / Offline Mode (No Key Required)": "StratagemAI-Engine",
        "Gemini": "gemini-2.5-flash",
        "OpenAI": "gpt-4o-mini",
        "Groq": "llama-3.3-70b-versatile",
    }
    
    model_name = st.text_input("Model Identifier", value=default_models.get(provider, "qwen2.5-coder:7b"))

    api_key = ""
    base_url = ""

    if provider == "Local Ollama (qwen2.5-coder:7b)":
        base_url = "http://localhost:11434/v1"
        api_key = "ollama"
        st.success("Local Ollama connected at localhost:11434")
    elif "Demo" in provider:
        st.info("Running in Offline Mode.")
    else:
        api_key_env_map = {
            "Gemini": "GOOGLE_API_KEY",
            "OpenAI": "OPENAI_API_KEY",
            "Groq": "GROQ_API_KEY",
        }
        detected_key = os.getenv(api_key_env_map.get(provider, ""), "")
        api_key = st.text_input(f"{provider} API Key", value=detected_key, type="password")
        if "Groq" in provider:
            base_url = "https://api.groq.com/openai/v1"

    st.markdown("---")
    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)


# --- Main Header ---
st.markdown('<div class="planner-header">StratagemAI</div>', unsafe_allow_html=True)
st.markdown('<div class="planner-sub">Goal Decomposition, Dependency-Aware Execution, and Dynamic Replanning</div>', unsafe_allow_html=True)

# State initialization
if "active_plan" not in st.session_state:
    st.session_state.active_plan = None

engine = StratagemPlannerEngine(
    provider=provider,
    model_name=model_name,
    api_key=api_key.strip() if api_key.strip() else None,
    base_url=base_url.strip() if base_url.strip() else None,
    temperature=temperature,
)

# Preset Goals
if "stratagem_goal_input" not in st.session_state:
    st.session_state["stratagem_goal_input"] = "Enterprise RAG Pipeline"

def set_stratagem_goal(goal_text: str):
    st.session_state["stratagem_goal_input"] = goal_text

col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    st.button("Enterprise RAG Pipeline", use_container_width=True, on_click=set_stratagem_goal, args=("Enterprise RAG Pipeline",))
with col_g2:
    st.button("Market Intelligence Agent", use_container_width=True, on_click=set_stratagem_goal, args=("Autonomous Market Research Engine",))
with col_g3:
    st.button("Autonomous Coding Agent", use_container_width=True, on_click=set_stratagem_goal, args=("Architect and ship an autonomous coding agent with static analysis, test suite validation, and git commit hooks",))

goal_input = st.text_input(
    "Define your high-level objective:",
    key="stratagem_goal_input",
    placeholder="e.g. Architect and launch a multi-agent data visualization platform with real-time streaming",
)

col_plan_btn, _ = st.columns([1, 4])
with col_plan_btn:
    if st.button("Decompose & Generate Plan", type="primary", use_container_width=True):
        target_goal = st.session_state.get("stratagem_goal_input", "").strip()
        if target_goal:
            with st.spinner("StratagemAI is decomposing your goal into milestones..."):
                st.session_state.active_plan = engine.create_plan(target_goal)
                st.success("Plan synthesized successfully!")
        else:
            st.warning("Please enter a goal or select a preset above.")

# Display Active Plan
plan: ExecutionPlan = st.session_state.active_plan

if plan:
    st.markdown("---")
    st.markdown(f"### Objective: **{plan.goal}**")
    st.info(f"**Strategic Approach:** {plan.overview}")

    # Top Metrics
    total = len(plan.tasks)
    completed = sum(1 for t in plan.tasks if t.status == TaskStatus.COMPLETED)
    pending = sum(1 for t in plan.tasks if t.status == TaskStatus.PENDING)
    failed = sum(1 for t in plan.tasks if t.status == TaskStatus.FAILED)

    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Progress", f"{round((completed / total) * 100 if total else 0)}%", f"{completed}/{total} Completed")
    mc2.metric("Pending Milestones", pending)
    mc3.metric("Blocked/Failed", failed)
    mc4.metric("Replanning Events", len(plan.replan_history))

    st.markdown("---")
    # Action Bar
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1.5, 1.5, 2])
    with ctrl_col1:
        if st.button("Execute Next Pending Milestone", use_container_width=True, type="primary"):
            next_task = next((t for t in plan.tasks if t.status == TaskStatus.PENDING), None)
            if next_task:
                with st.spinner(f"Executing #{next_task.id}: {next_task.title}..."):
                    engine.execute_subtask(plan, next_task.id)
                    st.rerun()
            else:
                st.info("All milestones have been executed.")

    with ctrl_col2:
        if st.button("Run All Remaining Milestones", use_container_width=True):
            with st.spinner("Executing remaining pipeline milestones..."):
                for t in plan.tasks:
                    if t.status == TaskStatus.PENDING:
                        engine.execute_subtask(plan, t.id)
                st.rerun()

    # Dynamic Replanning Section
    with st.expander("Trigger Dynamic Replanning / Requirement Shift"):
        replan_reason = st.text_input(
            "Describe the constraint, failure, or new requirement:",
            placeholder="e.g. Third-party API rate-limited; must substitute local FAISS vector search and add caching layer."
        )
        if st.button("Apply Replanning & Mutate Roadmap"):
            if replan_reason.strip():
                with st.spinner("Re-evaluating downstream tasks..."):
                    engine.trigger_replan(plan, replan_reason.strip())
                    st.success("Plan roadmap successfully updated.")
                    st.rerun()

    st.markdown("### Execution Roadmap & Milestones")

    # Render Task Cards
    for task in plan.tasks:
        status_class = f"status-badge-{task.status.value.lower()}"
        deps = f"Prerequisites: #{', #'.join(map(str, task.dependencies))}" if task.dependencies else "Prerequisites: None (Root)"
        
        with st.expander(f"Milestone {task.id}: {task.title}  [{task.status.value}]", expanded=(task.status == TaskStatus.IN_PROGRESS or task.status == TaskStatus.COMPLETED)):
            st.markdown(f"**Assigned Role:** `{task.assigned_role}` | **{deps}**")
            st.markdown(f"**Objective:** {task.description}")
            
            if task.execution_notes:
                st.warning(task.execution_notes)

            if task.output:
                st.markdown("**Deliverable Output:**")
                st.markdown(task.output)

            # Manual task controls
            if task.status != TaskStatus.COMPLETED:
                if st.button(f"Execute Milestone #{task.id}", key=f"run_{task.id}"):
                    with st.spinner(f"Running Milestone #{task.id}..."):
                        engine.execute_subtask(plan, task.id)
                        st.rerun()

    # Final Dossier Export
    if completed > 0:
        st.markdown("---")
        st.markdown("### Project Implementation Dossier")
        dossier = engine.compile_final_dossier(plan)
        
        export_col1, export_col2 = st.columns([1, 4])
        with export_col1:
            st.download_button(
                label="Download Markdown Dossier",
                data=dossier,
                file_name=f"stratagem_dossier_{int(time.time())}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with export_col2:
            st.download_button(
                label="Export Plan JSON Schema",
                data=plan.model_dump_json(indent=2),
                file_name=f"stratagem_plan_{int(time.time())}.json",
                mime="application/json",
                use_container_width=True,
            )

        with st.expander("Preview Complete Executive Dossier"):
            st.markdown(dossier)
