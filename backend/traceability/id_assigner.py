from collections import defaultdict
class IDAssigner:
    def __init__(self):self.traceability_matrix={};self.counters=defaultdict(int)
    def generate_id(self,parent_id,element_type):
        if not element_type:raise ValueError('Element type required')
        prefix=f'{parent_id}.{element_type}' if parent_id else element_type
        self.counters[prefix]+=1;value=f'{prefix}-{self.counters[prefix]:03}'
        if parent_id:self.register_link(parent_id,value)
        return value
    def register_link(self,source_id,target_id):
        links=self.traceability_matrix.setdefault(source_id,[])
        if target_id not in links:links.append(target_id)
        return True
    def get_dependencies(self,root_id):
        seen={root_id};result=[];todo=list(self.traceability_matrix.get(root_id,[]))
        while todo:
            node=todo.pop(0)
            if node in seen:continue
            seen.add(node);result.append(node);todo.extend(self.traceability_matrix.get(node,[]))
        return result
