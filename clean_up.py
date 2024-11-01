from pymongo import MongoClient

# Database connection
MONGO_URI = "mongodb://localhost:27017/ecommerce_db"
client = MongoClient(MONGO_URI)
db = client["ecommerce_db"]

# Clear existing data
db["users"].delete_many({})
db["products"].delete_many({})
db["interactions"].delete_many({})

print("Existing data cleared.")