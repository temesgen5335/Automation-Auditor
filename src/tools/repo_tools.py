import ast
import os
import subprocess
import tempfile
from typing import Dict, List, Optional
import shutil
import hashlib

class RepoInvestigatorTools:
    """
    Forensic tools for analyzing GitHub repositories.
    Includes AST parsing for LangGraph structures and Git history analysis.
    """

    @staticmethod
    def calculate_repo_hashes(repo_path: str) -> Dict[str, str]:
        """Calculates SHA-256 hashes for all files in the repository."""
        hashes = {}
        for root, _, files in os.walk(repo_path):
            if ".git" in root: continue
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                try:
                    with open(file_path, "rb") as f:
                        file_hash = hashlib.sha256(f.read()).hexdigest()
                    hashes[rel_path] = file_hash
                except Exception:
                    continue
        return hashes

    @staticmethod
    def clone_repo(repo_url: str) -> str:
        """Clones a repository to a temporary directory."""
        temp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "clone", repo_url, temp_dir], check=True, capture_output=True)
            return temp_dir
        except subprocess.CalledProcessError as e:
            shutil.rmtree(temp_dir)
            raise Exception(f"Failed to clone repo: {e.stderr.decode()}")

    @staticmethod
    def get_git_log(repo_path: str) -> List[Dict]:
        """Extracts commit history from the repository."""
        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H|%an|%ad|%s", "--date=iso"],
                cwd=repo_path,
                check=True,
                capture_output=True,
                text=True
            )
            commits = []
            for line in result.stdout.strip().split("\n"):
                if not line: continue
                hash, author, date, message = line.split("|", 3)
                commits.append({
                    "hash": hash,
                    "author": author,
                    "date": date,
                    "message": message
                })
            return commits
        except subprocess.CalledProcessError as e:
            return []

    @staticmethod
    def analyze_git_history(commits: List[Dict]) -> Dict:
        """Analyzes commit history for atomicity vs monolithicity."""
        if not commits:
            return {"style": "unknown", "count": 0, "rationale": "No commits found."}
        
        count = len(commits)
        # Simple heuristic: if count > 5 and messages aren't all "init", it's likely atomic
        messages = [c["message"].lower() for c in commits]
        has_init_monolith = any("init" in m or "first commit" in m for m in messages) and count < 3
        
        style = "monolithic" if has_init_monolith else "atomic"
        if count == 1: style = "monolithic"
        
        return {
            "style": style,
            "count": count,
            "rationale": f"Found {count} commits. Style determined as {style} based on commit frequency and messages."
        }

    @staticmethod
    def analyze_graph_structure(repo_path: str, files_to_scan: Optional[List[str]] = None) -> Dict:
        """
        Uses AST to verify the existence of StateGraph and parallel wiring.
        If files_to_scan is provided, only those files are analyzed.
        """
        results = {
            "has_stategraph": False,
            "has_parallelism": False,
            "has_typed_state": False,
            "details": []
        }

        for root, _, files in os.walk(repo_path):
            if ".git" in root: continue
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                if files_to_scan is not None and rel_path not in files_to_scan:
                    continue
                
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r") as f:
                            tree = ast.parse(f.read())
                        
                        # Use a NodeVisitor to find specific LangGraph patterns
                        visitor = LangGraphVisitor()
                        visitor.visit(tree)
                        
                        if visitor.found_stategraph:
                            results["has_stategraph"] = True
                        if visitor.found_parallelism:
                            results["has_parallelism"] = True
                        if visitor.found_typed_state:
                            results["has_typed_state"] = True
                        
                        if visitor.found_stategraph:
                            results["details"].append(f"Found StateGraph in {file}")

                    except Exception as e:
                        continue
        
        return results

class LangGraphVisitor(ast.NodeVisitor):
    def __init__(self):
        self.found_stategraph = False
        self.found_parallelism = False
        self.found_typed_state = False
        self.graph_builder_names = set()

    def visit_ImportFrom(self, node):
        if node.module == "langgraph.graph":
            for alias in node.names:
                if alias.name == "StateGraph":
                    self.found_stategraph = True
        if node.module in ["typing", "pydantic", "typing_extensions"]:
            self.found_typed_state = True
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Look for builder = StateGraph(State)
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == "StateGraph":
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.graph_builder_names.add(target.id)
                        self.found_stategraph = True
        self.generic_visit(node)

    def visit_Call(self, node):
        # Look for builder.add_edge(["node1", "node2"], "node3") or similar list inputs implying fan-in
        # Or multiple edges from same node implying fan-out
        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_edge":
            # Simple check for list in arguments (fan-in pattern)
            for arg in node.args:
                if isinstance(arg, ast.List):
                    self.found_parallelism = True
        
        # Look for builder.add_node
        if isinstance(node.func, ast.Attribute) and node.func.attr == "add_node":
             if isinstance(node.func.value, ast.Name) and node.func.value.id in self.graph_builder_names:
                 self.found_stategraph = True
                 
        self.generic_visit(node)

if __name__ == "__main__":
    # Quick self-test logic can go here
    pass
