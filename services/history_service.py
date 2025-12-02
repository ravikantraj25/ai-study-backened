from db.mongo import history_collection
from datetime import datetime

def save_history(user_id: str, action_type: str, input_data, result_data):
    doc = {
        "user_id": user_id,
        "type": action_type,
        "input": input_data,
        "result": result_data,
        "created_at": datetime.utcnow()
    }
    history_collection.insert_one(doc)
