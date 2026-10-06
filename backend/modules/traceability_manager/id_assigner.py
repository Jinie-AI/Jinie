"""Stable hierarchical identifiers and dependency links for generated artifacts."""

from collections import defaultdict


class IDAssigner:
    def __init__(self):
        self.traceability_matrix = defaultdict(list)
        self._counters = defaultdict(int)

    def generate_id(self, parent_id: str, element_type: str) -> str:
        kind = "".join(ch for ch in element_type.upper() if ch.isalnum())
        if not kind:
            raise ValueError("element_type must contain letters or numbers")
        key = (parent_id, kind)
        self._counters[key] += 1
        suffix = f"{kind}-{self._counters[key]:03}"
        return f"{parent_id}-{suffix}" if parent_id else suffix

    def register_link(self, source_id: str, target_id: str) -> bool:
        if not source_id or not target_id:
            raise ValueError("Both traceability IDs are required")
        if target_id not in self.traceability_matrix[source_id]:
            self.traceability_matrix[source_id].append(target_id)
        return True

    def get_dependencies(self, root_id: str) -> list[str]:
        found, pending = [], list(self.traceability_matrix.get(root_id, []))
        while pending:
            dependency = pending.pop(0)
            if dependency in found:
                continue
            found.append(dependency)
            pending.extend(self.traceability_matrix.get(dependency, []))
        return found
