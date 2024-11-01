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
cart_collection = db["cart"]

# Helper function to check user role
def is_admin(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    return user and user.get("role") == "admin"

@app.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = get_jwt_identity()
    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        cart = {
            "user_id": user_id,
            "items": [],
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow()
        }
        cart_id = cart_collection.insert_one(cart).inserted_id
        cart["_id"] = cart_id

    item_found = False
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item_found = True
            break

    if not item_found:
        cart["items"].append({"product_id": ObjectId(product_id), "quantity": quantity})

    cart["updated_at"] = datetime.datetime.utcnow()
    cart_collection.update_one({"_id": cart["_id"]}, {"$set": cart})

    return jsonify({"message": "Item added to cart", "cart": format_id(cart)}), 200


@app.route("/cart", methods=["GET"])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()
    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        return jsonify({"message": "Cart is empty"}), 404

    detailed_items = []
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            product_data = {
                "product_id": str(item["product_id"]),
                "name": product["name"],
                "price": product["price"],
                "quantity": item["quantity"],
                "total_price": product["price"] * item["quantity"]
            }
            detailed_items.append(product_data)

    return jsonify({"cart": detailed_items}), 200


# 4. Remove Item from Cart
@app.route("/cart", methods=["DELETE"])
@jwt_required()
def remove_from_cart():
    user_id = get_jwt_identity()
    product_name = request.json.get("product_name")

    # Find the product by name
    product = products_collection.find_one({"name": product_name})
    if not product:
        return jsonify({"message": "Product not found"}), 404

    product_id = product["_id"]  # Get the product ID from the found product

    # Find the user's cart
    cart = cart_collection.find_one({"user_id": user_id})
    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    # Remove the specified product from the cart items
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]

    # Update the cart in the database
    cart["updated_at"] = datetime.datetime.utcnow()
    cart_collection.update_one({"_id": cart["_id"]}, {"$set": cart})

    # Convert ObjectId fields to string before returning
    return jsonify({"message": "Item removed from cart", "cart": format_id(cart)}), 200


# Helper function to format ObjectId for JSON response
def format_id(document):
    document["_id"] = str(document["_id"])
    return document


# 1. User Registration with Duplicate Check
@app.route("/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    # Check if email or name already exists
    if users_collection.find_one({"email": email}) or users_collection.find_one({"name": name}):
        return jsonify({"message": "Email or username already exists"}), 400

    hashed_password = generate_password_hash(password)
    user_data = {
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": data.get("role", "user"),  # Default to 'user' role
        "created_at": datetime.datetime.utcnow()
    }
    user_id = users_collection.insert_one(user_data).inserted_id
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


# 3. Add Product (Admin Only)
@app.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    user_id = get_jwt_identity()

    # Check if the user is an admin
    if not is_admin(user_id):
        return jsonify({"message": "Access denied: Admins only"}), 403

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
