import grpc
from restaurant import restaurant_pb2
from restaurant import restaurant_pb2_grpc

def test():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = restaurant_pb2_grpc.RestaurantServiceStub(channel)

        print("\n--- 1. TEST NOM (Accents, Majuscules, Flou) ---")
        # Test "Auberge" pour voir si ça contient le mot
        req = restaurant_pb2.SearchRequest(query="Aubergé &")
        resp = stub.SearchByName(req)
        print(f"Résultats pour 'Aubergé &': {len(resp.restaurants)} trouvés.")
        
        print("\n--- 2. TEST TYPE (Index 4 : Restaurant) ---")
        resp = stub.SearchByType(restaurant_pb2.TypeRequest(type_index=4))
        print(f"Nombre de 'Restaurants': {len(resp.restaurants)}")

        print("\n--- 3. TEST CATEGORIE (Index 7 : Cuisine traditionnelle) ---")
        resp = stub.SearchByCategorie(restaurant_pb2.CategorieRequest(cat_index=7))
        print(f"Cuisine traditionnelle: {len(resp.restaurants)}")

        print("\n--- 4. TEST LOCALISATION (Code Postal 44) ---")
        resp = stub.SearchByLocation(restaurant_pb2.LocationRequest(value="44"))
        print(f"Restos dans le 44: {len(resp.restaurants)}")

        print("\n--- 5. TEST CAPACITÉ (Minimum 50 couverts) ---")
        req = restaurant_pb2.CapacityRequest(value=50, search_min=True, field_type="couverts")
        resp = stub.SearchByCapacity(req)
        print(f"Restos >= 50 couverts: {len(resp.restaurants)}")

        print("\n--- 6. TEST OUVERTURE (Oui) ---")
        resp = stub.SearchByStatus(restaurant_pb2.StatusRequest(ouvert="oui"))
        print(f"Ouverts toute l'année: {len(resp.restaurants)}")

        print("\n--- 7. TEST ERREUR ---")
        req = restaurant_pb2.SearchRequest(query="ZyzYzY_Inconnu")
        resp = stub.SearchByName(req)
        if resp.error_message: print(f"Erreur attendue: {resp.error_message}")

if __name__ == '__main__':
    test()