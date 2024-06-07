from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

admins_collection = db["admins"]
config_collection = db["config"]
users_collection = db["users"]

def add_admin(user_id):
    admins_collection.update_one({"user_id": user_id}, {"$set": {"is_admin": True}}, upsert=True)

def remove_admin(user_id):
    admins_collection.update_one({"user_id": user_id}, {"$set": {"is_admin": False}}, upsert=True)

def is_admin(user_id):
    admin = admins_collection.find_one({"user_id": user_id})
    return admin and admin.get("is_admin", False)

def set_force_sub(channel_id):
    config_collection.update_one({"config": "force_sub_channel"}, {"$set": {"value": channel_id}}, upsert=True)

def get_force_sub():
    config = config_collection.find_one({"config": "force_sub_channel"})
    return config["value"] if config else None

def get_all_users():
    return list(users_collection.find())

def save_broadcast_message(message):
    users_collection.insert_one({"message": message})
