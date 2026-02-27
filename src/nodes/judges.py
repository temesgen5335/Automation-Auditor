import json
from typing import Dict, List
from langchain_openai import ChatOpenAI
from src.state import AgentState, JudicialOpinion, Evidence
from langchain_core.messages import SystemMessage, HumanMessage

def load_rubric():
    with open("rubric.json", "r") as f:
        return json.load(f)

def get_judge_model(judge_type: str):
    # Initialize model with structured output
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return llm.with_structured_output(JudicialOpinion)

def evidence_aggregator(state: AgentState) -> Dict:
    """Synchronizes evidence from all detectives."""
    # This node acts as a fan-in point.
    # It doesn't strictly need to do much since the state reducer handles merging,
    # but it can be used to format the evidence for the judges.
    return {}

def judge_node_factory(judge_type: str):
    """Factory to create judge nodes for Prosecutor, Defense, and TechLead."""
    
    def node(state: AgentState) -> Dict:
        rubric = load_rubric()
        evidences = state.get("evidences", {})
        
        # Format evidence for the prompt
        evidence_str = ""
        for source, items in evidences.items():
            evidence_str += f"\n--- {source} ---\n"
            for ev in items:
                evidence_str += f"- Goal: {ev.goal}\n  Found: {ev.found}\n  Content: {ev.content}\n  Rationale: {ev.rationale}\n"

        persona_prompts = {
            "Prosecutor": "You are the Prosecutor. Your philosophy is 'Trust No One. Assume Vibe Coding.' "
                          "Scrutinize the evidence for gaps, security flaws, and laziness. Be harsh but objective.",
            "Defense": "You are the Defense Attorney. Your philosophy is 'Reward Effort and Intent. Look for the Spirit of the Law.' "
                       "Highlight creative workarounds and deep thought even if implementation is imperfect.",
            "TechLead": "You are the Tech Lead. Your philosophy is 'Does it actually work? Is it maintainable?' "
                        "Evaluate architectural soundness and practical viability. You are the pragmatic tie-breaker."
        }

        judge_model = get_judge_model(judge_type)
        
        opinions = []
        for dimension in rubric["dimensions"]:
            system_msg = SystemMessage(content=f"{persona_prompts[judge_type]}\n\n"
                                               f"Rubric Dimension: {dimension['name']}\n"
                                               f"Description: {dimension['description']}\n"
                                               f"Criteria: {', '.join(dimension['criteria'])}")
            
            human_msg = HumanMessage(content=f"Analyze the following evidence and provide your opinion:\n{evidence_str}")
            
            try:
                opinion = judge_model.invoke([system_msg, human_msg])
                # Ensure fields are correctly populated
                opinion.judge = judge_type
                opinion.criterion_id = dimension["id"]
                opinions.append(opinion)
            except Exception as e:
                # Fallback or retry logic could go here
                print(f"Error for {judge_type}: {e}")
        
        return {"opinions": opinions}
    
    return node

prosecutor_node = judge_node_factory("Prosecutor")
defense_node = judge_node_factory("Defense")
tech_lead_node = judge_node_factory("TechLead")
