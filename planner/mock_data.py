"""
Preset Planning Blueprints for StratagemAI testing and demonstration.
"""

from planner.models import ExecutionPlan, SubTask, TaskStatus

PRESET_PLANS = {
    "Enterprise RAG Pipeline": ExecutionPlan(
        goal="Design and Deploy an Enterprise-Grade Local RAG & Voice Assistant System",
        overview="Structured roadmap detailing document ingestion, vector indexing, retrieval fine-tuning, audio streaming, and frontend orchestration.",
        tasks=[
            SubTask(
                id=1,
                title="Architecture & Protocol Specification",
                description="Define data flows between FastAPI backend, LangChain chains, ChromaDB storage, and React/Streamlit clients.",
                dependencies=[],
                assigned_role="Lead Architect",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=2,
                title="Document Processing & Chunking Strategy",
                description="Implement semantic chunking with overlap thresholds for PDF, Markdown, and CSV technical specifications.",
                dependencies=[1],
                assigned_role="Data Engineer",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=3,
                title="Vector Database & Similarity Tuning",
                description="Deploy ChromaDB vector store with cosine distance metric and configure top-k retrieval parameters.",
                dependencies=[2],
                assigned_role="MLOps Engineer",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=4,
                title="Streaming Synthesis & ReAct Fallbacks",
                description="Connect LLM streaming completion with Server-Sent Events (SSE) and web search fallback tools.",
                dependencies=[3],
                assigned_role="AI Engineer",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=5,
                title="End-to-End Verification & Latency Benchmarking",
                description="Run simulated QA queries, measure TTFT (Time to First Token), and compile the final deployment dossier.",
                dependencies=[4],
                assigned_role="QA Lead",
                status=TaskStatus.PENDING,
            ),
        ]
    ),
    "Autonomous Market Research Engine": ExecutionPlan(
        goal="Build an Autonomous Competitive Intelligence Agent for SaaS Platforms",
        overview="Multi-phase plan spanning web scraping, sentiment extraction, feature comparison matrix generation, and executive reporting.",
        tasks=[
            SubTask(
                id=1,
                title="Competitor Identification & Landscape Mapping",
                description="Compile top 5 competitors in target vertical, mapping product tiers and public pricing.",
                dependencies=[],
                assigned_role="Market Researcher",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=2,
                title="Feature Matrix & Review Aggregation",
                description="Mine user reviews and tech specs to construct a quantitative feature comparison matrix.",
                dependencies=[1],
                assigned_role="Data Analyst",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=3,
                title="SWOT Analysis & Gap Discovery",
                description="Evaluate Strengths, Weaknesses, Opportunities, and Threats for our product relative to the market.",
                dependencies=[2],
                assigned_role="Strategist",
                status=TaskStatus.PENDING,
            ),
            SubTask(
                id=4,
                title="Executive Roadmap Synthesis",
                description="Generate actionable go-to-market priorities and product feature roadmap in Markdown.",
                dependencies=[3],
                assigned_role="Product Manager",
                status=TaskStatus.PENDING,
            ),
        ]
    )
}
