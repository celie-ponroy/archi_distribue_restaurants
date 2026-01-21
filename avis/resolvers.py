from pymongo import MongoClient

import grpc
from restaurant import restaurant_pb2
from restaurant import restaurant_pb2_grpc

restaurant_api = 'localhost:50051'
with grpc.insecure_channel(restaurant_api) as channel:
        stub = restaurant_pb2_grpc.RestaurantServiceStub(channel)


#bd avis
client = MongoClient("mongodb://localhost:27017/")
db = client["archiDistriRestaurants"]
avis_collection = db["avis"]


# restaurants proxy
# user proxy


# GET 
def get_all_avis():
    return list(avis_collection.find())


def get_avis_by_id(_,info,avis_id):
    #todo
    print("todo")

def get_avis_by_restaurant(_,info,restaurant_id):
    restaurant_pb2.SearchByName()
    #todo
    print("todo")

def get_avis_by_user(_,info,user):
    #todo
    print("todo")
def get_avis_by_rating(_,info,rating):
    #todo
    print("todo")


#MODIFY
def update_avis(_,info,avis_id, rating):
    #todo
    print("todo")

def create_avis(_,info,restaurant_id, user, rating, comment):
    #todo
    print("todo")


#DELETE
def delete_avis(_,info,avis_id):
    #todo
    print("todo")