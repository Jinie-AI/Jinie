from datetime import datetime,timezone
class CustomerFeedback:
    def __init__(self):self.items=[]
    def route_feedback(self,target_module,item_id,feedback_text):
        if not all([target_module,item_id,feedback_text.strip()]):raise ValueError('Module, artifact ID and feedback are required')
        self.items.append({'module':target_module,'artifact':item_id,'text':feedback_text,'time':datetime.now(timezone.utc).isoformat(),'status':'needs_review'})
        return True
