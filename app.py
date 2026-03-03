import streamlit as st
import os
import time
import glob
from langgraph.checkpoint.sqlite import SqliteSaver
from main import create_auditor_graph
from src.utils.checkpoint_manager import CheckpointManager

# --- Page Config ---
st.set_page_config(
    page_title="Automaton Auditor: Visual Dashboard",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    .node-log {
        font-family: 'Courier New', Courier, monospace;
        color: #10b981;
        background-color: #000000;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #059669;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("🔍 Auditor Controls")
repo_url = st.sidebar.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo")
pdf_path = st.sidebar.text_input("PDF Report Path (optional)", value="report.pdf")
thread_id = st.sidebar.text_input("Thread ID (for resumption)", value="streamlit-audit")

st.sidebar.divider()
st.sidebar.info("The Auditor Swarm uses a hierarchical LangGraph architecture to forensicly examine agentic codebases.")

# --- Initialization ---
if 'log' not in st.session_state:
    st.session_state.log = []

# --- Main App Tabs ---
tab1, tab2, tab3 = st.tabs(["🚀 Live Audit", "📚 Audit History", "⛓️ LangSmith Traces"])

with tab1:
    st.title("⚖️ Swarm Surveillance")
    
    if st.button("🚀 Commence Forensic Audit", type="primary", use_container_width=True):
        if not repo_url:
            st.error("Please provide a repository URL.")
        else:
            st.session_state.log = []
            log_placeholder = st.empty()
            progress_bar = st.progress(0)
            
            with SqliteSaver.from_conn_string("audit_checkpoints.sqlite") as checkpointer:
                app = create_auditor_graph(checkpointer)
                config = {"configurable": {"thread_id": thread_id}}
                
                initial_state = {
                    "repo_url": repo_url,
                    "pdf_path": pdf_path,
                    "rubric_dimensions": [],
                    "evidences": {},
                    "opinions": [],
                    "file_hashes": {},
                    "is_delta_audit": False,
                    "changed_files": []
                }
                
                # Execution Stream
                start_time = time.time()
                try:
                    total_expected_nodes = 10 # Estimated
                    nodes_executed = 0
                    
                    with st.status("🕵️ Swarm is actively investigating...", expanded=True) as status:
                        for output in app.stream(initial_state, config=config):
                            for node_name in output.keys():
                                nodes_executed += 1
                                current_log = f"[{time.strftime('%H:%M:%S')}] Swarm arrived at: **{node_name}**"
                                st.session_state.log.append(current_log)
                                st.write(current_log)
                                
                                # Update progress (clamped to 100%)
                                progress = min(nodes_executed / total_expected_nodes, 1.0)
                                progress_bar.progress(progress)
                                
                        status.update(label="✅ Audit Complete!", state="complete", expanded=False)
                    
                    st.success(f"Audit finished in {time.time() - start_time:.2f} seconds.")
                    
                    # Redirect suggestion
                    st.info("Navigate to the **Audit History** tab to view the generated report.")
                    
                except Exception as e:
                    st.error(f"Audit aborted due to error: {str(e)}")

with tab2:
    st.title("📂 Audit Repository")
    
    # List files in audits directory
    reports = glob.glob("audits/audit_report_*.md")
    reports.sort(reverse=True) # Newest first
    
    if not reports:
        st.warning("No audit reports found. Run your first audit to see history.")
    else:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Previous Reports")
            selected_report = st.selectbox("Select a session", reports, label_visibility="collapsed")
            
            # Extract basic info from filename/cache
            if selected_report:
                filename = os.path.basename(selected_report)
                st.info(f"Viewing: `{filename}`")
                
                # Try to find corresponding cache for visualization
                # Note: This is a bit decoupled, but we can try to find a repo that matches
                with open(selected_report, "r") as f:
                    first_line = f.readline()
                    if "Audit Report:" in first_line:
                        target_repo = first_line.replace("# Audit Report: ", "").strip()
                        metadata = CheckpointManager.get_audit_metadata(target_repo)
                        if metadata and "report" in metadata:
                            report_data = metadata["report"]
                            st.metric("Overall Score", f"{report_data['overall_score']}/5.0")
                            
                            # Bar chart of criteria
                            criteria_names = [c["dimension_name"] for c in report_data["criteria"]]
                            criteria_scores = [c["final_score"] for c in report_data["criteria"]]
                            st.bar_chart(dict(zip(criteria_names, criteria_scores)))

        with col2:
            if selected_report:
                with open(selected_report, "r") as f:
                    content = f.read()
                st.markdown(content)

with tab3:
    st.title("⛓️ Traceability Layer")
    st.markdown("""
    The Auditor Swarm is deeply integrated with **LangSmith**. 
    Click the link below to view end-to-end traces, node-level performance, and judicial reasoning logs.
    """)
    
    project_url = f"https://smith.langchain.com/o/10x-trp/projects/p/automation-auditor" # Placeholder or dynamic if possible
    st.link_button("🌐 Open LangSmith Console", project_url)
    
    st.divider()
    st.image("https://python.langchain.com/img/langsmith_logo.png", width=200)
