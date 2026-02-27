import os
from dotenv import load_dotenv
from typing import Dict, TypedDict, Annotated, List
import operator

from langgraph.graph import StateGraph, END
from src.state import AgentState, AuditReport
from src.nodes.detectives import repo_investigator_node, doc_analyst_node, vision_inspector_node
from src.nodes.judges import prosecutor_node, defense_node, tech_lead_node, evidence_aggregator
from src.nodes.supreme_court import chief_justice_node, generate_markdown_report

# Load environment variables
load_dotenv()

def create_auditor_graph():
    """Builds the hierarchical state graph for the Automaton Auditor."""
    workflow = StateGraph(AgentState)

    # 1. Add Detective Nodes
    workflow.add_node("repo_investigator", repo_investigator_node)
    workflow.add_node("doc_analyst", doc_analyst_node)
    workflow.add_node("vision_inspector", vision_inspector_node)
    
    # 2. Add Aggregator (Fan-in point for detectives)
    workflow.add_node("evidence_aggregator", evidence_aggregator)

    # 3. Add Judicial Nodes
    workflow.add_node("prosecutor", prosecutor_node)
    workflow.add_node("defense", defense_node)
    workflow.add_node("tech_lead", tech_lead_node)

    # 4. Add Supreme Court Node (Fan-in point for judges)
    workflow.add_node("supreme_court", chief_justice_node)

    # --- Edge Wiring (Hierarchical Swarm) ---

    # Entry point node for fan-out
    workflow.add_node("start", lambda x: x)
    workflow.set_entry_point("start")
    
    # Parallel Detectives (Fan-out)
    workflow.add_edge("start", "repo_investigator")
    workflow.add_edge("start", "doc_analyst")
    workflow.add_edge("start", "vision_inspector")

    # Fan-in Detectives to Aggregator
    workflow.add_edge("repo_investigator", "evidence_aggregator")
    workflow.add_edge("doc_analyst", "evidence_aggregator")
    workflow.add_edge("vision_inspector", "evidence_aggregator")
    
    # Parallel Judges (Fan-out)
    workflow.add_edge("evidence_aggregator", "prosecutor")
    workflow.add_edge("evidence_aggregator", "defense")
    workflow.add_edge("evidence_aggregator", "tech_lead")

    # Fan-in Judges to Supreme Court (Synthesis)
    workflow.add_edge("prosecutor", "supreme_court")
    workflow.add_edge("defense", "supreme_court")
    workflow.add_edge("tech_lead", "supreme_court")

    workflow.add_edge("supreme_court", END)

    return workflow.compile()

if __name__ == "__main__":
    # Example usage
    app = create_auditor_graph()
    
    initial_state = {
        "repo_url": "https://github.com/langchain-ai/langgraph",
        "pdf_path": "report.pdf", # Placeholder
        "rubric_dimensions": [], # Dynamically loaded in judges
        "evidences": {},
        "opinions": []
    }
    
    print("Automaton Auditor Swarm Initialized.")
    print("Graph compiled successfully. Ready for Governor-level audits.")
