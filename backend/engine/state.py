"""Reusable artifact store; Studio persists complete projects through studio.store."""
from copy import deepcopy
class CurrentState:
    def __init__(self):self.state_data={}
    def get_artifact(self,artifact_id):
        if artifact_id not in self.state_data:raise KeyError(artifact_id)
        return deepcopy(self.state_data[artifact_id])
    def update_artifact(self,artifact_id,new_value):
        if not artifact_id:raise ValueError('Artifact ID is required')
        self.state_data[artifact_id]=deepcopy(new_value);return True
    def clear_state(self):self.state_data.clear()
