from flask import Flask, request, jsonify
from pymongo import MongoClient
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


def format_id(document):
    document["_id"] = str(document["_id"])
    return document


# 1. User Registration with Password Hashing
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


from bson import ObjectId
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/user/history", methods=["GET"])
@jwt_required()
def get_user_history():
    # Retrieve the current user's ID as a string
    user_id = str(get_jwt_identity())
    print("User ID for history retrieval:", user_id)  # Debugging line

    # Query interactions using user_id as a string
    interactions = list(interactions_collection.find({"user_id": user_id}).sort("timestamp", -1))
    print("Interactions retrieved:", interactions)  # Debugging line

    if not interactions:
        print("No interactions found for user:", user_id)
        return jsonify({"message": "No interactions found"}), 404

    # Convert product_ids to ObjectId for querying products_collection
    product_ids = [ObjectId(interaction["product_id"]) for interaction in interactions]
    products = {str(product["_id"]): product for product in products_collection.find({"_id": {"$in": product_ids}})}
    print("Products retrieved based on interactions:", products)  # Debugging line

    # Build the history list with product details
    history = []
    for interaction in interactions:
        product_id = str(interaction["product_id"])
        product = products.get(product_id)
        if product:
            history_item = {
                "product": {
                    "name": product["name"],
                    "description": product["description"],
                    "category": product["category"],
                    "price": product["price"],
                },
                "interaction_type": interaction["interaction_type"],
                "timestamp": interaction["timestamp"]
            }
            print("History item added:", history_item)  # Debugging line
            history.append(history_item)
        else:
            print(f"Product with ID {product_id} not found in products collection")  # Debugging line

    return jsonify(history), 200

# 3. Protected Route: Add Product to Catalog
@app.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    data = request.json
    product_id = products_collection.insert_one(data).inserted_id
    return jsonify({"message": "Product added", "product_id": str(product_id)}), 201


# 4. Public Route: Get Product Catalog
@app.route("/products", methods=["GET"])
def get_products():
    products = list(products_collection.find())
    return jsonify([format_id(product) for product in products]), 200


# 5. Record User Interaction (view, like, purchase)
@app.route("/interactions", methods=["POST"])
@jwt_required()
def add_interaction():
    user_id = get_jwt_identity()
    data = request.json
    data["user_id"] = user_id
    data["timestamp"] = datetime.datetime.utcnow()
    interaction_id = interactions_collection.insert_one(data).inserted_id
    return jsonify({"message": "Interaction recorded", "interaction_id": str(interaction_id)}), 201


# 6. Get Recommendations for User
@app.route("/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()

    # Collaborative filtering: Find top products based on similar user interactions
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


# Protected Route: Logout (not required since JWTs are stateless)

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
