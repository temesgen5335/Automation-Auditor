from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run
from main import create_auditor_graph
from dotenv import load_dotenv

load_dotenv()

def audit_runner(inputs: dict) -> dict:
    """Wrapper to run the graph for LangSmith evaluation."""
    app = create_auditor_graph()
    result = app.invoke({
        "repo_url": inputs["repo_url"],
        "pdf_path": inputs["pdf_path"],
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": []
    })
    return {
        "overall_score": result["final_report"].overall_score,
        "summary": result["final_report"].executive_summary
    }

def score_similarity(run: Run, example: Example) -> dict:
    """Simple evaluator for score deviation."""
    predicted = run.outputs.get("overall_score")
    expected = example.outputs.get("expected_score")
    
    score = 1.0 - (abs(predicted - expected) / 5.0)
    return {"key": "score_accuracy", "score": max(0, score)}

def run_evaluation():
    dataset_name = "Automaton Auditor Benchmark"
    
    print(f"Starting evaluation sweep for: {dataset_name}")
    
    evaluate(
        audit_runner,
        data=dataset_name,
        evaluators=[score_similarity],
        experiment_prefix="swarm-deliberation",
        metadata={
            "version": "1.0",
            "layer": "synthetic-benchmark"
        }
    )

if __name__ == "__main__":
    # Ensure dataset exists before running
    # run_evaluation()
    print("Evaluator script ready. Ensure dataset is created first.")
