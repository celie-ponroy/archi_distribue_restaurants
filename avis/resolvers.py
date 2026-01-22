from restaurant_client import createQueryRequest, get_restaurant_client
from pymongo import MongoClient
import statistics
from bson.objectid import ObjectId
import requests


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
USER_URL = "http://web"


def _verify_token_is_admin(info):
    """Vérifie si le token dans le contexte a le statut admin"""
    # Récupère le token Bearer depuis l'en-tête Authorization du contexte Flask
    auth_header = None
    if info and getattr(info, "context", None):
        # Ariadne transmet l'objet Flask request via context_value
        auth_header = info.context.headers.get("Authorization") if hasattr(info.context, "headers") else None

    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise Exception("Token manquant dans l'en-tête Authorization")

    token = auth_header.split(" ", 1)[1]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{USER_URL}/authapi.php?check_admin=true", headers=headers)

    if response.status_code != 200:
        return False

    data = response.json()
    if data.get("data", {}).get("is_admin"):
        return True
    else:
        return False


def _verify_token_is_user(info, user):
    """Vérifie si le token dans le contexte correspond au user passé en paramètre"""
    # Récupère le token Bearer depuis l'en-tête Authorization du contexte Flask
    auth_header = None
    if info and getattr(info, "context", None):
        # Ariadne transmet l'objet Flask request via context_value
        auth_header = info.context.headers.get("Authorization") if hasattr(info.context, "headers") else None

    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise Exception("Token manquant dans l'en-tête Authorization")

    token = auth_header.split(" ", 1)[1]
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{USER_URL}/authapi.php?verify_login=true&login={user}", headers=headers)

    if response.status_code != 200:
        return False

    data = response.json()
    if data.get("data", {}).get("matches"):
        return True
    else:
        return False

# GET 
def get_avis_by_id(_, info, id_avis):
    _avis_collection = _get_mongo_client()
    return _avis_collection.find_one({'_id': ObjectId(id_avis)})

def get_all_avis(_, info):
    avis_collection = _get_mongo_client()
    return list(avis_collection.find())


def get_avis_by_restaurant(_, info, restaurant_id):
    _avis_collection = _get_mongo_client()
    return list(_avis_collection.find({"id_restaurant": restaurant_id}))

def get_avis_by_user(_, info, user_id):
    _avis_collection = _get_mongo_client()
    return list(_avis_collection.find({"user": user_id}))

def get_average_rate_by_restaurant(_,info, restaurant_id):
    _avis_collection = _get_mongo_client()
    return statistics.mean([avis["note"] for avis in list(_avis_collection.find({"id_restaurant": restaurant_id}))])

#MODIFY
#on peut modifier uniquement les note et les commentaires
def update_avis(_,info, id_avis, note,commentaire):
    # Récupère l'avis pour obtenir le user qui l'a créé
    _avis_collection = _get_mongo_client()
    avis = _avis_collection.find_one({"_id":ObjectId(id_avis)})
    
    if not avis:
        raise Exception("Avis non trouvé")
    
    user = avis["user"]
    
    # Vérifie que le token correspond à l'utilisateur qui a créé l'avis
    if(_verify_token_is_user(info, user)):
        _avis_collection.update_one({"_id":ObjectId(id_avis)},{"$set":{
            "note": note,
            "commentaire": commentaire
        }})
        return _avis_collection.find_one({"_id":ObjectId(id_avis)})
    else:
        raise Exception("Le token ne correspond pas à l'utilisateur")

def create_avis(_,info, restaurant_id, user_id, note, commentaire=None):
    #si le restaurant existe 
    if(_verify_token_is_user(info, user_id)):
        if(len(get_restaurant_client().SearchByName(createQueryRequest(query=restaurant_id)).restaurants) > 0): #ne fonctionne pas :(

            _avis_collection = _get_mongo_client()

            res = _avis_collection.insert_one({
                "id_restaurant": restaurant_id,
                "user": user_id,
                "note": note,
                "commentaire": commentaire
            })
            return _avis_collection.find_one({"_id":res.inserted_id})
        else:
            raise Exception("Le restaurant n'existe pas")
    else:
        raise Exception("Le token ne correspond pas à l'utilisateur")
    


#DELETE
def delete_avis(_,info, id):
    _avis_collection = _get_mongo_client()
    avis = _avis_collection.find_one({'_id': ObjectId(id)})
    if not avis:
        raise Exception("Avis non trouvé")
    user = avis['user']

    if(_verify_token_is_admin(info) or _verify_token_is_user(info, user)):
        _avis_collection = _get_mongo_client()
        _avis_collection.delete_one({'_id': ObjectId(id)})
        if(_avis_collection.find_one({'_id': ObjectId(id)}) is None):
            return "Avis supprimé avec succès"
        return "Erreur lors de la suppression de l'avis"
    else:
        raise Exception("Vous n'êtes ni l'auteur ni un administrateur")
