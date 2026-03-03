import os
import argparse
from dotenv import load_dotenv
from typing import Dict, TypedDict, Annotated, List, Literal
import operator

from langgraph.graph import StateGraph, END
from src.state import AgentState, AuditReport
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node, evidence_aggregator
from src.nodes.supreme_court import chief_justice_node, generate_markdown_report

# Load environment variables
load_dotenv()

def error_handler(state: AgentState) -> Dict:
    """Handles terminal error states in the graph."""
    print("\n!!! Auditor Swarm Encountered a Critical Error !!!")
    return {"executive_summary": "Audit aborted due to critical infrastructure failure (e.g., Git clone failed)."}

def check_detective_sanity(state: AgentState) -> Literal["proceed", "error"]:
    """Conditional edge to verify if detectives found minimal evidence to proceed."""
    evidences = state.get("evidences", {})
    repo_evidence = evidences.get("repo_evidence", [])
    if not repo_evidence or not any(ev.found for ev in repo_evidence):
        return "error"
    return "proceed"

def create_auditor_graph():
    """Builds the hierarchical state graph with robust error handling."""
    workflow = StateGraph(AgentState)

    workflow.add_node("start", lambda x: x)
    workflow.add_node("repo_investigator", repo_investigator_node)
    workflow.add_node("doc_analyst", doc_analyst_node)
    workflow.add_node("vision_inspector", vision_inspector_node)
    workflow.add_node("evidence_aggregator", evidence_aggregator)
    workflow.add_node("judge_trigger", lambda x: x)
    workflow.add_node("prosecutor", prosecutor_node)
    workflow.add_node("defense", defense_node)
    workflow.add_node("tech_lead", tech_lead_node)
    workflow.add_node("supreme_court", chief_justice_node)
    workflow.add_node("error_handling", error_handler)

    workflow.set_entry_point("start")
    workflow.add_edge("start", "repo_investigator")
    workflow.add_edge("start", "doc_analyst")
    workflow.add_edge("start", "vision_inspector")

    workflow.add_edge("repo_investigator", "evidence_aggregator")
    workflow.add_edge("doc_analyst", "evidence_aggregator")
    workflow.add_edge("vision_inspector", "evidence_aggregator")

    workflow.add_conditional_edges(
        "evidence_aggregator",
        check_detective_sanity,
        {
            "proceed": "judge_trigger",
            "error": "error_handling"
        }
    )
    
    workflow.add_edge("judge_trigger", "prosecutor")
    workflow.add_edge("judge_trigger", "defense")
    workflow.add_edge("judge_trigger", "tech_lead")

    workflow.add_edge("prosecutor", "supreme_court")
    workflow.add_edge("defense", "supreme_court")
    workflow.add_edge("tech_lead", "supreme_court")

    workflow.add_edge("supreme_court", END)
    workflow.add_edge("error_handling", END)

    return workflow.compile()

def main():
    parser = argparse.ArgumentParser(description="Automaton Auditor: Autonomous Governance Swarm")
    parser.add_argument("repo_url", help="The GitHub repository URL to audit")
    parser.add_argument("--pdf", help="Path to the PDF report (optional)", default="report.pdf")
    
    args = parser.parse_args()
    
    print(f"Initializing Auditor Swarm for: {args.repo_url}")
    
    app = create_auditor_graph()
    
    initial_state = {
        "repo_url": args.repo_url,
        "pdf_path": args.pdf,
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": []
    }
    
    # Run the swarm
    for output in app.stream(initial_state):
        # Optional: Print node activity for observability
        for node_name in output.keys():
            print(f"Node Executing: {node_name}")

if __name__ == "__main__":
    main()
