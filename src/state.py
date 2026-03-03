import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# --- Detective Output ---
class Evidence(BaseModel):
    goal: str = Field()
    found: bool = Field(description="Whether the artifact exists")
    content: Optional[str] = Field(default=None)
    location: str = Field(
        description="File path or commit hash",
    )
    rationale: str = Field(
        description="Your rationale for your confidence "
        "on the evidence you find for this particular goal",
    )
    confidence: float

# --- Judge Output ---
class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    criterion_id: str
    score: int = Field(ge=1, le=5)
    argument: str
    cited_evidence: List[str]

# --- Chief Justice Output ---
class CriterionResult(BaseModel):
    dimension_id: str
    dimension_name: str
    final_score: int = Field(ge=1, le=5)
    judge_opinions: List[JudicialOpinion]
    dissent_summary: Optional[str] = Field(
        default=None,
        description="Required when score variance > 2",
    )
    remediation: str = Field(
        description="Specific file-level instructions "
        "for improvement",
    )

class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult]
    remediation_plan: str
    delta_info: Optional[Dict] = Field(
        default=None,
        description="Metadata for differential reports (e.g., score changes, new files)"
    )

def merge_evidences(left: Dict[str, List[Evidence]], right: Dict[str, List[Evidence]]) -> Dict[str, List[Evidence]]:
    """Merges evidence dictionaries by appending lists for matching keys."""
    combined = left.copy()
    for key, value in right.items():
        if key in combined:
            combined[key] = combined[key] + value
        else:
            combined[key] = value
    return combined

# --- Graph State ---
class AgentState(TypedDict):
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[Dict]
    # Use custom reducer to merge evidence lists
    evidences: Annotated[
        Dict[str, List[Evidence]], merge_evidences
    ]
    opinions: Annotated[
        List[JudicialOpinion], operator.add
    ]
    final_report: AuditReport
    
    # Delta & Caching Fields
    file_hashes: Dict[str, str]
    is_delta_audit: bool
    previous_audit_report: Optional[AuditReport]
    changed_files: List[str]
    temp_repo_path: Optional[str] # ephemeral field
