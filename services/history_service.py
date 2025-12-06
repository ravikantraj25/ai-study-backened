from db.mongo import history_collection
from datetime import datetime, timezone

def save_history(user_id: str, action_type: str, input_data, result_data):
    """
    Saves a user's interaction to the MongoDB 'history' collection.
    Designed to run as a Background Task.
    """
    try:
        doc = {
            "user_id": user_id,
            "type": action_type,
            "input": input_data,
            "result": result_data,
            # Uses modern timezone-aware UTC (Best practice)
            "created_at": datetime.now(timezone.utc)
        }
        
        history_collection.insert_one(doc)
        
        # Optional: Uncomment this line if you want to see confirmations in your terminal
        # print(f"✅ History saved for {action_type}")

    except Exception as e:
        # This is crucial for background tasks so you know if something breaks
        print(f"❌ Error saving history: {e}")