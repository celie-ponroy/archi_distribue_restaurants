from restaurant_client import get_restaurant_client
from pymongo import MongoClient
import statistics


restaurant = get_restaurant_client()
_client = None
_avis_collection = None
def _get_mongo_client():
    global _client, _avis_collection
    if _client is None:
        try:
            _client = MongoClient("mongodb://mongo_database:27017", serverSelectionTimeoutMS=5000)
            _avis_collection = _client["archiDistriRestaurants"]["avis"]
        except Exception:
            _client = None
            _avis_collection = None
            raise Exception("Impossible de se connecter à la base de données.")
    return _avis_collection



# restaurants proxy
# user proxy


# GET 
def get_all_avis(_, info):
    avis_collection = _get_mongo_client()
    return list(avis_collection.find())


def get_avis_by_restaurant(_, info, restaurant_id):
    _avis_collection = _get_mongo_client()
    return list(_avis_collection.find({"id_restaurant": restaurant_id}))

def get_avis_by_user(_, info, user_id):
    _avis_collection = _get_mongo_client()
    return list(_avis_collection.find({"user": user_id}))

def get_average_rate_by_restaurant(_, restaurant_id):
    _avis_collection = _get_mongo_client()
    return statistics.mean([avis["note"] for avis in list(_avis_collection.find({"id_restaurant": restaurant_id}))])

#MODIFY
def update_avis(_, id, note,commentaire):
    _avis_collection = _get_mongo_client()
    return _avis_collection.update_one({_id:id},{
        "note": note,
        "commentaire": commentaire
    })

def create_avis(_, info, restaurant_id, user_id, note, commentaire=None):
    _avis_collection = _get_mongo_client()
    return(_avis_collection.insert_one({
        "id_restaurant": restaurant_id,
        "user": user_id,
        "note": note,
        "commentaire": commentaire
    }))


#DELETE
def delete_avis(_, info):
    pass