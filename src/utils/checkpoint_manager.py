import json
import os
from typing import Dict, Optional, List
from src.state import AuditReport

CACHE_DIR = "audits/cache"
CACHE_FILE = os.path.join(CACHE_DIR, "audit_metadata.json")

class CheckpointManager:
    @staticmethod
    def init_cache():
        os.makedirs(CACHE_DIR, exist_ok=True)
        if not os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "w") as f:
                json.dump({}, f)

    @staticmethod
    def get_audit_metadata(repo_url: str) -> Optional[Dict]:
        CheckpointManager.init_cache()
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        return cache.get(repo_url)

    @staticmethod
    def save_audit_metadata(repo_url: str, file_hashes: Dict[str, str], report: AuditReport):
        CheckpointManager.init_cache()
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
        
        cache[repo_url] = {
            "file_hashes": file_hashes,
            "report": report.dict(),
            "last_audited": os.path.getmtime(CACHE_FILE) # Simple timestamp
        }
        
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)

    @staticmethod
    def get_changed_files(repo_url: str, current_hashes: Dict[str, str]) -> List[str]:
        metadata = CheckpointManager.get_audit_metadata(repo_url)
        if not metadata:
            return list(current_hashes.keys())
        
        previous_hashes = metadata.get("file_hashes", {})
        changed_files = []
        
        for path, h in current_hashes.items():
            if path not in previous_hashes or previous_hashes[path] != h:
                changed_files.append(path)
                
        return changed_files
