from typing import Dict, List
from src.state import AgentState, Evidence
from src.tools.repo_tools import RepoInvestigatorTools
from src.tools.doc_tools import DocAnalystTools
from src.tools.vision_tools import VisionInspectorTools
import os
import shutil

def repo_investigator_node(state: AgentState) -> Dict:
    """Collects evidence from the GitHub repository."""
    repo_url = state["repo_url"]
    tools = RepoInvestigatorTools()
    
    # Forensic Protocol: Clone, analyze history, and AST
    repo_path = tools.clone_repo(repo_url)
    try:
        commits = tools.get_git_log(repo_path)
        git_analysis = tools.analyze_git_history(commits)
        ast_analysis = tools.analyze_graph_structure(repo_path)
        
        # Create Evidence objects
        evidences = []
        evidences.append(Evidence(
            goal="Identify Git Narrative",
            found=len(commits) > 0,
            content=git_analysis["style"],
            location="git log",
            rationale=git_analysis["rationale"],
            confidence=1.0
        ))
        
        evidences.append(Evidence(
            goal="Verify Graph Structure",
            found=ast_analysis["has_stategraph"],
            content=f"Parallelism: {ast_analysis['has_parallelism']}",
            location="AST Analysis",
            rationale=", ".join(ast_analysis["details"]) or "No StateGraph found in AST.",
            confidence=0.9
        ))
        
        return {"evidences": {"repo_evidence": evidences}}
    finally:
        # Cleanup cloned repo
        shutil.rmtree(repo_path)

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
