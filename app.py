from flask import Flask, request, jsonify
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from config import MONGO_URI, DATABASE_NAME, JWT_SECRET_KEY
import datetime

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
jwt = JWTManager(app)

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
users_collection = db["users"]
products_collection = db["products"]
interactions_collection = db["interactions"]


# Helper function to format ObjectId for JSON response
def format_id(document):
    document["_id"] = str(document["_id"])
    return document


# 1. User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    data["password"] = generate_password_hash(data["password"])
    user_id = users_collection.insert_one(data).inserted_id
    return jsonify({"message": "User registered", "user_id": str(user_id)}), 201


# 2. User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})

    if user and check_password_hash(user["password"], data["password"]):
        access_token = create_access_token(identity=str(user["_id"]))
        return jsonify({"access_token": access_token}), 200
    return jsonify({"message": "Invalid credentials"}), 401


# 3. User Profile Retrieval and Update
@app.route("/profile", methods=["GET", "PUT"])
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    if request.method == "GET":
        user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        return jsonify(format_id(user)), 200

    elif request.method == "PUT":
        data = request.json
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": data})
        return jsonify({"message": "Profile updated"}), 200


# 4. Add Product to Catalog
@app.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    data = request.json
    product_id = products_collection.insert_one(data).inserted_id
    return jsonify({"message": "Product added", "product_id": str(product_id)}), 201


# 5. Get Product Catalog with Search
@app.route("/products", methods=["GET"])
def get_products():
    query = {}
    name = request.args.get("name")
    category = request.args.get("category")

    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    if category:
        query["category"] = category

    products = list(products_collection.find(query))
    return jsonify([format_id(product) for product in products]), 200


# 6. Record User Interaction (view, like, purchase)
@app.route("/interactions", methods=["POST"])
@jwt_required()
def add_interaction():
    user_id = get_jwt_identity()
    data = request.json
    data["user_id"] = user_id
    data["timestamp"] = datetime.datetime.utcnow()
    interaction_id = interactions_collection.insert_one(data).inserted_id
    return jsonify({"message": "Interaction recorded", "interaction_id": str(interaction_id)}), 201


# 7. Get User Interaction History
@app.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    interactions = list(interactions_collection.find({"user_id": user_id}).sort("timestamp", DESCENDING))
    return jsonify([format_id(interaction) for interaction in interactions]), 200


# 8. Get Recommendations for User (Collaborative Filtering)
@app.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()

    # Collaborative filtering based on item-based interactions
    # Find popular products among other users who interacted with the same items
    pipeline = [
        {"$match": {"user_id": {"$ne": user_id}}},
        {"$group": {"_id": "$product_id", "interactions_count": {"$sum": 1}}},
        {"$sort": {"interactions_count": -1}},
        {"$limit": 5}
    ]
    popular_products = list(interactions_collection.aggregate(pipeline))
    product_ids = [ObjectId(item["_id"]) for item in popular_products]
    recommendations = products_collection.find({"_id": {"$in": product_ids}})

    return jsonify({
        "user_id": user_id,
        "recommendations": [format_id(product) for product in recommendations]
    }), 200


# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
