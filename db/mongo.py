from pymongo import MongoClient
import certifi
import os

# -----------------------------
# 🔐 Load MongoDB URI
# If environment variable exists, use it
# Else fall back to your current hardcoded URI
# -----------------------------
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://princegaurav384_db_user:Ravikant384@ai-study-cluster.b6keteg.mongodb.net/?retryWrites=true&w=majority&appName=ai-study-cluster"
)

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())

# -----------------------------
# 📌 Main Database
# -----------------------------
db = client["ai-study-db"]

# -----------------------------
# 📘 Collections
# -----------------------------
notes_collection = db["notes"]

# 👤 For user accounts
users_collection = db["users"]

# 📜 For history (summaries, notes, mcq, qna)
history_collection = db["history"]
