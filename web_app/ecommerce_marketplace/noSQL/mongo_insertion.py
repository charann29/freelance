from pymongo import MongoClient
from datetime import datetime

# MongoDB connection URI
mongo_uri = "mongodb://localhost:27017/"
database_name = "ecommerce_db"  # Replace with your database name

# Sample data
users_data = [
    { 
        "user_id": 1, 
        "username": "seller 1", 
        "password": "password", 
        "email": "examplemail@mail.com", 
        "city": "Sarajevo", 
        "image": "default.jpg", 
        "balance": 1000, 
        "role": "user", 
        "location": "Sarajevo" 
    },
    { 
        "user_id": 2, 
        "username": "seller 2", 
        "password": "password", 
        "email": "examplemail2@gmail.com", 
        "city": "Tuzla", 
        "image": "default.jpg", 
        "balance": 1000, 
        "role": "user", 
        "location": "Tuzla" 
    },
    { 
        "user_id": 3, 
        "username": "seller 3", 
        "password": "password", 
        "email": "examplemail3@mail.com", 
        "city": "Sarajevo", 
        "image": "default.jpg", 
        "balance": 1000, 
        "role": "user", 
        "location": "Sarajevo" 
    }
]

products_data = [
    { 
        "product_id": 1, 
        "user_id": 1, 
        "title": "iPhone", 
        "image": "iphone.jpg", 
        "description": "This is a test iphone", 
        "price": 599, 
        "created_at": datetime.now(), 
        "category": "Phones", 
        "user_name": "seller 1", 
        "avg_review": 4.5, 
        "location": "Sarajevo" 
    },
    { 
        "product_id": 2, 
        "user_id": 1, 
        "title": "Laptop", 
        "image": "laptop.jpg", 
        "description": "This is a test laptop", 
        "price": 1400, 
        "created_at": datetime.now(), 
        "category": "Laptops", 
        "user_name": "seller 1", 
        "avg_review": 4.0, 
        "location": "Sarajevo" 
    },
    # Add more products as needed
]

reviews_data = [
    { 
        "review_id": 1, 
        "product_id": 1, 
        "user_id": 2, 
        "rating": 5, 
        "created_at": datetime.now(), 
        "username": "seller 2" 
    },
    # Add more reviews as needed
]

comments_data = [
    { 
        "comment_id": 1, 
        "user_id": 1, 
        "content": "test comment", 
        "created_at": datetime.now(), 
        "product_id": 2, 
        "username": "seller 1" 
    },
    # Add more comments as needed
]

carts_data = [
    { 
        "id": 1, 
        "product_id": 1, 
        "user_id": 1 
    },
    # Add more carts as needed
]

# Connect to MongoDB
client = MongoClient(mongo_uri)
db = client[database_name]

# Insert data into collections
db.users.insert_many(users_data)
db.products.insert_many(products_data)
db.reviews.insert_many(reviews_data)
db.comments.insert_many(comments_data)
db.carts.insert_many(carts_data)

# Close MongoDB connection
client.close()

print("Data inserted successfully.")
