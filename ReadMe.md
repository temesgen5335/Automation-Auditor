# Automaton Auditor

The Automaton Auditor is a production-grade multi-agent swarm built with LangGraph for autonomous governance of AI-generated code.

## Architecture: The Digital Courtroom
The system operates as a hierarchical graph with three distinct layers:

1. Detective Layer (Forensic Sub-Agents):

* RepoInvestigator: Uses Python's ast module to verify code structure and git log for process analysis.
* DocAnalyst: Uses Docling to parse PDF reports and extract theoretical depth.
* VisionInspector: (Skeleton) Extracts diagrams for multimodal architectural verification.

2. Judicial Layer (The Dialectical Bench):

* Prosecutor: Critical lens, focuses on security and "vibe coding."
* Defense: Optimistic lens, rewards effort and intent.
* Tech Lead: Pragmatic lens, evaluates technical debt and viability.
* These judges run in parallel and use structured output to provide scores and arguments.

3. Supreme Court (Synthesis Engine):

* ChiefJusticeNode: Resolves conflicts between judges using hardcoded deterministic rules (e.g., Rule of Security, Rule of Evidence).
* Generates a final structured Audit Report in Markdown.

### Key Features
* Fan-out/Fan-in Orchestration: Parallel detectives and parallel judges synchronized via LangGraph.
* Typed State Management: Uses Pydantic and TypedDict with custom reducers (operator.add, operator.ior) to prevent data overwriting in parallel branches.
* Forensic Precision: Moves beyond simple RAG by using specialized tools for code and document analysis.

### Project Structure
text

Automation_Auditor/
├── src/
│   ├── state.py          # Core Pydantic schemas and AgentState
│   ├── nodes/
│   │   ├── detectives.py # Detective nodes
│   │   ├── judges.py     # Judicial nodes & persona logic
│   │   └── supreme_court.py # Synthesis & report generation
│   └── tools/
│       ├── repo_tools.py # AST & Git forensic tools
│       ├── doc_tools.py  # Docling PDF parsing
│       └── vision_tools.py # Vision extraction
├── main.py               # LangGraph orchestration
├── rubric.json           # Dynamic scoring criteria
└── pyproject.toml        # uv configuration

### Verification Results
* Infrastructure: Project initialized with uv, dependencies managed.
* State Schema: Verified via Pydantic model validation.
* Graph Wiring: Fan-out/Fan-in branches verified in 
main.py
.
 Forensic Tools: 
RepoInvestigatorTools
 (AST) and 
DocAnalystTools
 (Docling) integrated.
 
Built with LangChain, LangGraph, and LangSmith.