import os
from langsmith import Client
from dotenv import load_dotenv

load_dotenv()

def create_audit_dataset():
    client = Client()
    dataset_name = "Automaton Auditor Benchmark"
    
    # Check if dataset exists
    if client.has_dataset(dataset_name=dataset_name):
        print(f"Dataset '{dataset_name}' already exists.")
        return
    
    # Create dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description="Evaluation dataset for Automaton Auditor swarms."
    )
    
    # Define example inputs and expected results
    # Each example maps to the AgentState's initial fields
    examples = [
        {
            "inputs": {
                "repo_url": "https://github.com/langchain-ai/langgraph",
                "pdf_path": "report.pdf"
            },
            "outputs": {
                "expected_score": 4.5,
                "notes": "LangGraph repo should score high on architecture."
            }
        },
        {
            "inputs": {
                "repo_url": "https://github.com/openai/openai-python",
                "pdf_path": "report.pdf"
            },
            "outputs": {
                "expected_score": 4.0,
                "notes": "Well-structured production library."
            }
        },
        {
            "inputs": {
                "repo_url": "https://github.com/vibe-coding/buggy-example", # Mock URL
                "pdf_path": "report.pdf"
            },
            "outputs": {
                "expected_score": 2.0,
                "notes": "Simulated low quality repo."
            }
        }
    ]
    
    for ex in examples:
        client.create_example(
            inputs=ex["inputs"],
            outputs=ex["outputs"],
            dataset_id=dataset.id
        )
    
    print(f"Dataset '{dataset_name}' created successfully with {len(examples)} examples.")

if __name__ == "__main__":
    create_audit_dataset()
