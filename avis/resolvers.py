from restaurant_client import get_restaurant_client
from pymongo import MongoClient

restaurant = get_restaurant_client()

def _get_mongo_client():
    global _client, _avis_collection
    if _client is None:
        _client = MongoClient("mongodb://mongo_database:27017/", serverSelectionTimeoutMS=5000)
        _avis_collection = _client["archiDistriRestaurants"]["avis"]
    return _avis_collection



# restaurants proxy
# user proxy


# GET 
def get_all_avis(_, info):
    avis_collection = _get_mongo_client()
    return list(avis_collection.find())


def get_avis_by_id(_, info, _id):
    pass

def get_avis_by_restaurant(_, info, _restaurant_id):
    pass

def get_avis_by_user(_, info, _user_id):
    pass

def get_average_rate_by_restaurant(_, info, _restaurant_id):
    pass


#MODIFY
def update_avis(_, info, _id, _rate):
    pass

def create_avis(_, info, _restaurant_id, _user_id, _rate, _comment=None):
    pass


#DELETE
def delete_avis(_, info, _id):
    pass