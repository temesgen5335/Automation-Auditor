# Testing Guide: Automaton Auditor

Follow these steps to verify and run the Automaton Auditor swarm with the high-point configuration.

## 1. Prerequisites
- **Python 3.10+** (managed via `uv`)
- **API Keys**: Ensure `.env` has active `OPENAI_API_KEY` and `LANGSMITH_API_KEY`.
- **Dependencies**: Run `uv sync` to ensure all packages (LangGraph, Docling, Gitingest, etc.) are installed.

### Resilience & Efficiency
- **Checkpointing**: Uses SQL-based persistence to resume interrupted audits exactly where they left off.
- **Delta Analysis**: Only analyzes files that have changed since the last audit, significantly reducing token consumption.
- **Differential Reporting**: Highlights score changes and regressions between successive audits.

## 🧪 Testing Commands
Run the main orchestration script with the target repository URL:
```bash
# Full Audit
python3 main.py https://github.com/user/repo --pdf report.pdf

# Delta Audit (Run again on same repo)
python3 main.py https://github.com/user/repo --pdf report.pdf

# Resumption (If interrupted)
python3 main.py https://github.com/user/repo --thread-id session-1
```

You can also specify a custom PDF report path:
```bash
uv run python main.py https://github.com/username/repo --pdf path/to/report.pdf
```

## 2. Configuration
The swarm uses `rubric.json` for scoring. You can modify this file to test different evaluation criteria.

## 3. Execution
### What to Expect:
1.  **Detective Layer (Fan-out)**: The system clones and analyzes the repository.
2.  **Evidence Aggregation (Fan-in)**: Evidence is collected and validated.
3.  **Judicial Layer (Fan-out)**: The Prosecutor, Defense, and Tech Lead personas deliberate in parallel.
4.  **Supreme Court (Synthesis)**: A final verdict is reached.
5.  **Output**: A structured Markdown report is saved in the **`audits/`** folder with a timestamped filename (e.g., `audits/audit_report_20240303_191000.md`).

## 4. Verifying High-Point Criteria
- **Check Parallelism**: Look at LangSmith traces to see the parallel execution branches for both detectives and judges.

## Resilience Features

### 1. Persistent Checkpointing
The swarm now supports `SqliteSaver` persistence. If an audit is interrupted (e.g., network failure, process killed), you can resume it using the `--thread-id` flag.
```bash
python3 main.py <repo_url> --thread-id audit-001
```

### 2. Delta Audits & Hashing
The `CheckpointManager` stores SHA-256 hashes of all repository files. Subsequent audits of the same repository will:
1. Detect which files have changed.
2. Only run `RepoInvestigator` tools on modified files.
3. Generate a **Differential Report** highlighting score swings.

### 3. Monitoring with LangSmith
Traces are automatically sent to the `automation-auditor` LangSmith project for node-level debugging.
- **Check Error Handling**: Run the script with a broken repo URL to verify the `Conditional Edge` triggers the `error_handling` node.
- **Check Synthesis Rules**:
    - Force a low Prosecution score for security to see the 3.0 cap in `audit_report.md`.
    - Provide a repository without a `StateGraph` but a high Defense claim to see the `Evidence Rule` in action.

## 5. Vision Analysis (Optional)
To enable visual diagram analysis, provide a path to a PDF with architectural diagrams in `main.py`. The `VisionInspector` will extract images and (if a multimodal client is provided) evaluate the flow.
