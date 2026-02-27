from typing import Dict, List
from src.state import AgentState, AuditReport, CriterionResult, JudicialOpinion, Evidence
import json

def chief_justice_node(state: AgentState) -> Dict:
    """
    Synthesizes judicial opinions into a final verdict.
    Resolves conflicts using hardcoded deterministic logic.
    """
    opinions = state.get("opinions", [])
    evidences = state.get("evidences", {})
    repo_url = state["repo_url"]
    
    # Group opinions by criterion
    grouped_opinions: Dict[str, List[JudicialOpinion]] = {}
    for op in opinions:
        if op.criterion_id not in grouped_opinions:
            grouped_opinions[op.criterion_id] = []
        grouped_opinions[op.criterion_id].append(op)
    
    criterion_results = []
    
    for crit_id, ops in grouped_opinions.items():
        # Identify opinions by persona
        prosecutor = next((op for op in ops if op.judge == "Prosecutor"), None)
        defense = next((op for op in ops if op.judge == "Defense"), None)
        tech_lead = next((op for op in ops if op.judge == "TechLead"), None)
        
        # Hardcoded Deliberation Protocols
        final_score = tech_lead.score if tech_lead else 3
        dissent_summary = None
        
        # Rule of Security: Prosecutor overrides if score is 1
        if prosecutor and prosecutor.score == 1:
            final_score = min(final_score, 3)
            dissent_summary = "Security Rule: Prosecutor identified critical flaws. Score capped."
        
        # Rule of Functionality: Tech Lead weight for Architecture
        if crit_id == "langgraph_arch" and tech_lead:
            final_score = tech_lead.score
            
        # Rule of Evidence: Overrule defense if evidence is missing
        repo_evidence = evidences.get("repo_evidence", [])
        has_graph = any(ev.found for ev in repo_evidence if "Graph" in ev.goal)
        if defense and defense.score > 3 and not has_graph:
            final_score = min(final_score, 2)
            dissent_summary = "Evidence Rule: Defense claims of merit not supported by repository artifacts."

        # Calculate variance for dissent summary
        scores = [op.score for op in ops]
        if max(scores) - min(scores) > 2 and not dissent_summary:
            dissent_summary = f"High Variance: Significant disagreement between judges (Range: {min(scores)}-{max(scores)})."

        criterion_results.append(CriterionResult(
            dimension_id=crit_id,
            dimension_name=crit_id.replace("_", " ").title(), # Simplified mapping
            final_score=final_score,
            judge_opinions=ops,
            dissent_summary=dissent_summary,
            remediation=tech_lead.argument if tech_lead else "Improve modularity and structure."
        ))

    overall_score = sum(r.final_score for r in criterion_results) / len(criterion_results) if criterion_results else 0
    
    final_report = AuditReport(
        repo_url=repo_url,
        executive_summary="Automaton Auditor has completed the forensic analysis and judicial deliberation.",
        overall_score=overall_score,
        criteria=criterion_results,
        remediation_plan="\n".join([f"- {r.dimension_name}: {r.remediation}" for r in criterion_results])
    )
    
    return {"final_report": final_report}

def generate_markdown_report(report: AuditReport) -> str:
    """Converts the AuditReport object into a formatted Markdown string."""
    md = f"# Audit Report: {report.repo_url}\n\n"
    md += f"## Overall Score: {report.overall_score:.1f}/5.0\n\n"
    md += f"### Executive Summary\n{report.executive_summary}\n\n"
    
    md += "## Criterion Breakdown\n"
    for crit in report.criteria:
        md += f"### {crit.dimension_name}\n"
        md += f"- **Final Score:** {crit.final_score}/5\n"
        if crit.dissent_summary:
            md += f"- **Judicial Dissent:** {crit.dissent_summary}\n"
        md += f"- **Remediation:** {crit.remediation}\n\n"
        
        md += "#### Judicial Options\n"
        for op in crit.judge_opinions:
            md += f"- **{op.judge}:** (Score: {op.score}) {op.argument}\n"
        md += "\n"
        
    md += f"## Remediation Plan\n{report.remediation_plan}\n"
    return md
