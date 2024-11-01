from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from config import MONGO_URI, DATABASE_NAME

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]
products_collection = db["products"]

# Sample Users
users = [
    {"name": "Alice", "email": "alice@example.com", "password": generate_password_hash("password1")},
    {"name": "Bob", "email": "bob@example.com", "password": generate_password_hash("password2")},
    {"name": "Charlie", "email": "charlie@example.com", "password": generate_password_hash("password3")},
    {"name": "Diana", "email": "diana@example.com", "password": generate_password_hash("password4")}
]

# Insert users
users_collection.insert_many(users)
print("Users inserted")

# Sample Products
products = [
    {"name": "Laptop", "description": "A high-end gaming laptop", "category": "Electronics", "price": 1500.99},
    {"name": "Smartphone", "description": "Latest model with excellent camera", "category": "Electronics", "price": 999.99},
    {"name": "Headphones", "description": "Noise-canceling headphones", "category": "Audio", "price": 199.99},
    {"name": "Smartwatch", "description": "Track your fitness and notifications", "category": "Wearable", "price": 299.99},
    {"name": "Camera", "description": "Professional DSLR camera", "category": "Photography", "price": 1200.00},
    {"name": "Tablet", "description": "Portable and powerful tablet", "category": "Electronics", "price": 400.00},
    {"name": "Desk Lamp", "description": "LED lamp with adjustable brightness", "category": "Home", "price": 29.99},
    {"name": "Backpack", "description": "Durable and stylish backpack", "category": "Accessories", "price": 49.99},
    {"name": "Gaming Mouse", "description": "Precision mouse with RGB lighting", "category": "Electronics", "price": 59.99},
    {"name": "Mechanical Keyboard", "description": "Tactile and durable keyboard", "category": "Electronics", "price": 89.99},
    {"name": "Coffee Maker", "description": "Brew the perfect cup of coffee", "category": "Kitchen", "price": 79.99},
    {"name": "Microwave", "description": "Compact microwave with quick heat settings", "category": "Kitchen", "price": 149.99},
    {"name": "Vacuum Cleaner", "description": "High suction vacuum cleaner", "category": "Home", "price": 199.99},
    {"name": "Blender", "description": "High-speed blender for smoothies", "category": "Kitchen", "price": 69.99},
    {"name": "Yoga Mat", "description": "Non-slip yoga mat", "category": "Fitness", "price": 25.99},
    {"name": "Treadmill", "description": "Electric treadmill for indoor workouts", "category": "Fitness", "price": 599.99},
    {"name": "Camping Tent", "description": "Spacious tent for 4 people", "category": "Outdoor", "price": 129.99},
    {"name": "Binoculars", "description": "High-quality binoculars for outdoor adventures", "category": "Outdoor", "price": 89.99},
    {"name": "Electric Scooter", "description": "Eco-friendly electric scooter", "category": "Transportation", "price": 450.00},
    {"name": "Mountain Bike", "description": "Durable bike for off-road trails", "category": "Fitness", "price": 850.00}
]

# Insert products
products_collection.insert_many(products)
print("Products inserted")
