from typing import Dict, List
from src.state import AgentState, Evidence, AuditReport
from src.tools.repo_tools import RepoInvestigatorTools
from src.tools.doc_tools import DocAnalystTools
from src.tools.vision_tools import VisionInspectorTools
from src.utils.checkpoint_manager import CheckpointManager
import shutil
import os

def pre_audit_check(state: AgentState) -> Dict:
    """
    Clones the repo, checks cache, and identifies changed files.
    """
    repo_url = state["repo_url"]
    
    # 1. Clone repo to get current state
    repo_path = RepoInvestigatorTools.clone_repo(repo_url)
    
    # 2. Calculate current hashes
    current_hashes = RepoInvestigatorTools.calculate_repo_hashes(repo_path)
    
    # 3. Check for previous audit
    metadata = CheckpointManager.get_audit_metadata(repo_url)
    
    is_delta = False
    changed_files = list(current_hashes.keys())
    previous_report = None
    
    if metadata:
        is_delta = True
        changed_files = CheckpointManager.get_changed_files(repo_url, current_hashes)
        previous_report = AuditReport(**metadata["report"])
        
    return {
        "is_delta_audit": is_delta,
        "file_hashes": current_hashes,
        "changed_files": changed_files,
        "previous_audit_report": previous_report,
        "temp_repo_path": repo_path # Pass the path forward to avoid re-cloning
    }

def repo_investigator_node(state: AgentState) -> Dict:
    """
    Analyzes the repository for LangGraph patterns.
    Supports delta audits by only scanning changed files.
    """
    repo_path = state.get("temp_repo_path")
    if not repo_path:
        repo_path = RepoInvestigatorTools.clone_repo(state["repo_url"])
    
    changed_files = state.get("changed_files", [])
    
    # Analyze graph structure (only scanning changed/new files)
    graph_structure = RepoInvestigatorTools.analyze_graph_structure(repo_path, files_to_scan=changed_files)
    
    # Analyze Git history
    commits = RepoInvestigatorTools.get_git_log(repo_path)
    git_style = RepoInvestigatorTools.analyze_git_history(commits)
    
    # Cleanup if not using it further (but we might need it for vision/docs)
    # For now, let's keep it and cleanup at the end of the node or graph.
    
    evidence = [
        Evidence(
            goal="Identify LangGraph Orchestration",
            found=graph_structure["has_stategraph"],
            content=str(graph_structure["details"]),
            location="Multiple Files",
            rationale="AST analysis of StateGraph instantiation.",
            confidence=0.9
        ),
        Evidence(
            goal="Verify Parallel Wiring",
            found=graph_structure["has_parallelism"],
            content="Detected explicit fan-out/fan-in connectivity or list-based edges.",
            location="Multiple Files",
            rationale="Aggressive AST connectivity analysis of add_edge calls.",
            confidence=0.95
        ),
        Evidence(
            goal="Identify State Reducers",
            found=graph_structure["has_reducers"],
            content="Detected operator imports or Annotated reducer patterns.",
            location="Multiple Files",
            rationale="AST scan for Annotated types with multi-argument slices.",
            confidence=0.9
        ),
        Evidence(
            goal="Analyze Git Style",
            found=True,
            content=git_style["style"],
            location="Git Log",
            rationale=git_style["rationale"],
            confidence=1.0
        )
    ]
    
    return {"evidences": {"repo_evidence": evidence}}

def doc_analyst_node(state: AgentState) -> Dict:
    """Collects evidence from the PDF report."""
    pdf_path = state["pdf_path"]
    tools = DocAnalystTools()
    
    try:
        text = tools.ingest_pdf(pdf_path)
        
        # Forensic Protocol: Check for key concepts
        keywords = ["Parallel", "Dialectical", "Synthesis", "Metacognition"]
        concept_context = tools.query_context(text, keywords)
        
        evidence = Evidence(
            goal="Verify Theoretical Depth",
            found=len(concept_context) > 0,
            content=concept_context[:500] + "...",
            location=pdf_path,
            rationale="Scanned document for keywords related to advanced agentic architectures.",
            confidence=0.8
        )
        
        return {"evidences": {"doc_evidence": [evidence]}}
    except Exception as e:
        return {"evidences": {"doc_evidence": [Evidence(
            goal="PDF Ingestion",
            found=False,
            location=pdf_path,
            rationale=f"Error parsing PDF: {str(e)}",
            confidence=0.0
        )]}}

def vision_inspector_node(state: AgentState) -> Dict:
    """Skeleton for architectural diagram analysis."""
    # Optional logic for Phase 2
    return {"evidences": {"vision_evidence": []}}
