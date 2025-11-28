from pymongo import MongoClient
import certifi

MONGO_URI = "mongodb+srv://princegaurav384_db_user:Ravikant384@ai-study-cluster.b6keteg.mongodb.net/?retryWrites=true&w=majority&appName=ai-study-cluster"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["ai-study-db"]
notes_collection = db["notes"]

