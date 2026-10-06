"""Module 02 state adapter backed by Jinie's configured project store."""

from copy import deepcopy

from modules.utilities import store


class CurrentState:
    def get_artifact(self, artifact_id: str) -> dict:
        return deepcopy(store.get(artifact_id))

    def update_artifact(self, artifact_id: str, new_value: dict) -> bool:
        if new_value.get("id") not in (None, artifact_id):
            raise ValueError("Artifact ID does not match the project payload")
        project = deepcopy(new_value)
        project["id"] = artifact_id
        store.save(project)
        return True

    def clear_state(self) -> None:
        """Deliberately unsupported: project deletion requires an explicit API operation."""
        raise RuntimeError("Bulk project deletion is not supported")
