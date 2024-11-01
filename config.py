# config.py
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/ecommerce_db")
DATABASE_NAME = "ecommerce_db"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key")
