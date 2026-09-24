"""Structural checks only; behavior is tested separately."""
from pathlib import Path
import json
class VerificationValidation:
    def __init__(self,root='.',traceability=None):self.root=Path(root).resolve();self.traceability=traceability or {}
    def verify_artifact(self,artifact_id):
        path=(self.root/artifact_id).resolve()
        if not path.is_relative_to(self.root) or not path.is_file() or path.stat().st_size==0:return False
        if path.suffix=='.json':
            try:json.loads(path.read_text())
            except (ValueError,UnicodeError):return False
        return True
    def validate_requirement(self,requirement_id,artifact_id):
        return artifact_id in self.traceability.get(requirement_id,[]) and self.verify_artifact(artifact_id)
