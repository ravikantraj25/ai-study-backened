import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

print("DEBUG MONGO URI:", MONGO_URI)   # 🔥 ADD THIS

client = MongoClient(MONGO_URI)

db = client["ai_study_database"]

notes_collection = db["notes"]
qna_collection = db["qna"]
