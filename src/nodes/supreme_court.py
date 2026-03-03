from typing import Dict, List
from src.state import AgentState, AuditReport, CriterionResult, JudicialOpinion, Evidence
import json
import os
from datetime import datetime

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
        
        # Hardcoded Deliberation Protocols (High-Point Criteria)
        # 1. Functionality Weight: Tech Lead carries highest weight for architecture
        final_score = tech_lead.score if tech_lead else 3
        dissent_summary = None
        
        # 2. Security Override: Prosecutor identifies confirmed security vulnerability
        if prosecutor and prosecutor.score == 1:
            # Security flaws cap the score at 3 regardless of Tech Lead/Defense
            final_score = min(final_score, 3)
            dissent_summary = "Security Rule: Critical vulnerability detected by Prosecutor. Score capped."
        
        # 3. Evidence Rule: Detectors overrule unsupported judge claims
        repo_evidence = evidences.get("repo_evidence", [])
        has_graph = any(ev.found for ev in repo_evidence if "Graph" in ev.goal)
        if defense and defense.score > 3 and not has_graph:
            # If Defense claims merit but RepoInvestigator found no graph, overrule for hallucination
            final_score = min(final_score, 2)
            dissent_summary = "Evidence Rule: Defense claims of merit overridden due to lack of repository evidence."

        # Variance check for mandatory dissent summary
        scores = [op.score for op in ops]
        if scores and (max(scores) - min(scores) > 2) and not dissent_summary:
            dissent_summary = f"High Variance Rule: Judges strongly disagreed ({min(scores)} to {max(scores)}). tech Lead as tie-breaker."

        criterion_results.append(CriterionResult(
            dimension_id=crit_id,
            dimension_name=crit_id.replace("_", " ").title(),
            final_score=final_score,
            judge_opinions=ops,
            dissent_summary=dissent_summary,
            remediation=tech_lead.argument if tech_lead else "Remediation pending further analysis."
        ))

    overall_score = sum(r.final_score for r in criterion_results) / len(criterion_results) if criterion_results else 0
    
    final_report = AuditReport(
        repo_url=repo_url,
        executive_summary="Swarm-level forensic audit complete. Dialectical conflict resolved via Supreme Court protocols.",
        overall_score=float(f"{overall_score:.2f}"),
        criteria=criterion_results,
        remediation_plan="\n".join([f"- {r.dimension_name}: {r.remediation}" for r in criterion_results])
    )
    
    # Write to file (High-Point Requirement) - Now with timestamped folder
    os.makedirs("audits", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"audits/audit_report_{timestamp}.md"
    
    report_md = generate_markdown_report(final_report)
    with open(report_filename, "w") as f:
        f.write(report_md)
    
    print(f"\nAudit completed. Report saved to: {report_filename}")
    
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
