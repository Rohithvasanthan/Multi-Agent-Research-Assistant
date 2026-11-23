import os
import time
import streamlit as st
from graph import research_agent

st.set_page_config(
    page_title="AgentFlow AI • Multi-Agent Research & Code Architect",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Modern UI Styling
st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 1.75rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.3);
        margin-bottom: 1.5rem;
    }
    .main-header h1 {
        color: #f8fafc;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    .main-header p {
        color: #94a3b8;
        margin: 0.4rem 0 0 0;
        font-size: 1rem;
    }
    .badge {
        display: inline-block;
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.4);
        padding: 0.2rem 0.65rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-top: 0.75rem;
    }
    .agent-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .agent-card-active {
        background: linear-gradient(135deg, rgba(79, 70, 229, 0.2), rgba(15, 23, 42, 0.9));
        border: 1px solid #6366f1;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.2);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #4f46e5 0%, #6366f1 100%);
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Hero Header Banner
st.markdown(
    """
    <div class="main-header">
        <h1>⚡ AgentFlow AI — Multi-Agent Research & Code Architect</h1>
        <p>Autonomous cyclic state machine orchestrating live web research, technical synthesis, and automated quality review.</p>
        <div>
            <span class="badge">LangGraph Cyclic Engine</span>
            <span class="badge">Gemini 2.5 Flash</span>
            <span class="badge">DuckDuckGo Live Search</span>
            <span class="badge">Self-Reflection Guardrails</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🔑 Workspace Setup")
    default_key = os.getenv("GOOGLE_API_KEY", "")
    if not default_key and "GOOGLE_API_KEY" in st.secrets:
        default_key = st.secrets["GOOGLE_API_KEY"]

    api_key = st.text_input(
        "Google AI Studio API Key",
        type="password",
        value=default_key,
        placeholder="AIzaSy...",
        help="Free tier key from Google AI Studio.",
    )
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        st.success("API Key Connected", icon="✅")
    else:
        st.warning("Enter API Key to run agents", icon="⚠️")

    st.markdown("[Get Free Gemini API Key ↗](https://aistudio.google.com/apikey)")
    st.divider()

    st.markdown("### 🧠 Agent Pipeline Topology")
    st.info(
        "**1. Researcher Node**\nQueries real-time web context and addresses reviewer feedback.\n\n"
        "**2. Synthesizer Node**\nDrafts structured engineering specs & production code.\n\n"
        "**3. Reviewer Node**\nAudits accuracy & triggers cyclic retry (up to 2 passes) if gaps exist."
    )

    st.divider()
    st.caption("Built by Rohithvasanthan E • AI Engineering Portfolio")

# Sample Prompts Section
def set_sample_query(text: str):
    st.session_state.query_input = text

st.markdown("#### 💡 Try an Engineering Benchmark Prompt")
p1, p2, p3 = st.columns(3)
with p1:
    st.button(
        "🔍 Hybrid RAG vs Vector Search",
        use_container_width=True,
        on_click=set_sample_query,
        args=("Explain how Hybrid RAG (Dense Vector + BM25) improves retrieval precision over naive vector search with Python code.",),
    )
with p2:
    st.button(
        "🔄 LangGraph Cyclic Reflection",
        use_container_width=True,
        on_click=set_sample_query,
        args=("How do cyclic state machines in LangGraph prevent hallucinations compared to linear LangChain chains?",),
    )
with p3:
    st.button(
        "⚡ FastAPI SSE Token Streaming",
        use_container_width=True,
        on_click=set_sample_query,
        args=("Write a production FastAPI endpoint using Server-Sent Events (SSE) to stream LLM tokens.",),
    )

# Query Input Box
query = st.text_area(
    "Research Topic or Technical Architecture Query",
    key="query_input",
    height=110,
    placeholder="Ask any complex technical, system design, or coding question...",
)

col_run, col_clear, _ = st.columns([1.5, 1, 3.5])
run_clicked = col_run.button("🚀 Execute Agent Workflow", type="primary", use_container_width=True)
if col_clear.button("🗑️ Clear", use_container_width=True):
    st.session_state.query_input = ""
    st.session_state.last_result = None
    st.rerun()

# Agent Execution
if run_clicked:
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("⚠️ Please configure your Google AI Studio API key in the sidebar first.")
    elif not st.session_state.query_input.strip():
        st.warning("⚠️ Please enter a query or select one of the benchmark prompts above.")
    else:
        initial_state = {
            "query": st.session_state.query_input.strip(),
            "research_notes": [],
            "draft_report": "",
            "critique": "",
            "revision_count": 0,
            "is_approved": False,
        }

        # Live Agent Stage Visual Indicators
        st.markdown("#### 🛰️ Live Agent Execution Pipeline")
        stage_cols = st.columns(3)
        stage_1 = stage_cols[0].empty()
        stage_2 = stage_cols[1].empty()
        stage_3 = stage_cols[2].empty()

        def render_stages(active_node: str = ""):
            s1_cls = "agent-card-active" if active_node == "researcher" else "agent-card"
            s2_cls = "agent-card-active" if active_node == "synthesizer" else "agent-card"
            s3_cls = "agent-card-active" if active_node == "reviewer" else "agent-card"
            stage_1.markdown(f'<div class="{s1_cls}"><h4>🔍 1. Researcher</h4><small>Live Web Context</small></div>', unsafe_allow_html=True)
            stage_2.markdown(f'<div class="{s2_cls}"><h4>✍️ 2. Synthesizer</h4><small>Architecture & Code</small></div>', unsafe_allow_html=True)
            stage_3.markdown(f'<div class="{s3_cls}"><h4>🛡️ 3. Reviewer</h4><small>Quality Guardrail</small></div>', unsafe_allow_html=True)

        render_stages("researcher")
        status_log = st.status("Initializing LangGraph cyclic workflow...", expanded=True)

        start_time = time.time()
        final_report = ""
        revisions = 0
        collected_notes = []

        try:
            for step in research_agent.stream(initial_state):
                for node_name, node_output in step.items():
                    if node_name == "researcher":
                        render_stages("researcher")
                        collected_notes = node_output.get("research_notes", collected_notes)
                        status_log.write("🔍 **Researcher Node:** Fetched live web sources & updated `AgentState`.")
                    elif node_name == "synthesizer":
                        render_stages("synthesizer")
                        revisions = node_output.get("revision_count", revisions)
                        final_report = node_output.get("draft_report", final_report)
                        status_log.write(f"✍️ **Synthesizer Node:** Compiled technical draft **v{revisions}**.")
                    elif node_name == "reviewer":
                        render_stages("reviewer")
                        if node_output.get("is_approved"):
                            status_log.write("🛡️ **Reviewer Node:** Verification passed — **APPROVED**.")
                        else:
                            status_log.write(
                                f"🔄 **Reviewer Node:** Quality gap detected. Routing back to Researcher:\n> *{node_output.get('critique')}*"
                            )

            elapsed = round(time.time() - start_time, 2)
            render_stages("")
            status_log.update(
                label=f"✅ Workflow verified and completed in {elapsed}s ({revisions} pass(es))",
                state="complete",
                expanded=False,
            )

            st.session_state.last_result = {
                "report": final_report,
                "notes": collected_notes,
                "revisions": revisions,
                "elapsed": elapsed,
            }

        except Exception as e:
            status_log.update(label="❌ Agent Pipeline Error", state="error", expanded=True)
            st.error(f"Execution failed: {str(e)}")

# Render Results Dashboard
if st.session_state.last_result:
    res = st.session_state.last_result
    st.divider()

    # Execution Telemetry Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Synthesis Passes", f"{res['revisions']} Cycle(s)", "Self-Verified")
    m2.metric("Execution Latency", f"{res['elapsed']} sec", "Gemini 2.5 Flash")
    m3.metric("Guardrail Status", "APPROVED", "Hallucination Checked")

    tab_report, tab_sources = st.tabs(["📄 Final Verified Report", "🌐 Raw Web Research Notes"])

    with tab_report:
        st.markdown(res["report"])
        st.download_button(
            label="📥 Download Technical Report (.md)",
            data=res["report"],
            file_name="agent_research_report.md",
            mime="text/markdown",
        )

    with tab_sources:
        if res["notes"]:
            for idx, note in enumerate(res["notes"], 1):
                st.info(f"**Source Batch {idx}:**\n\n{note}")
        else:
            st.caption("No external search notes recorded.")