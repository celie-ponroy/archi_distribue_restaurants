import grpc
import restaurant_pb2
import restaurant_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = restaurant_pb2_grpc.RestaurantServiceStub(channel)
        
        # TEST 1 : Cache
        print("\n--- ⚡️ TEST 1 : LISTE GLOBALE (CACHE RAM) ---")
        response = stub.GetAllRestaurants(restaurant_pb2.Empty())
        print(f"Reçu {len(response.restaurants)} restaurants instantanément.")
        if len(response.restaurants) > 0:
            print(f"Exemple: {response.restaurants[0].name}")

        # TEST 2 : Live API
        ville = "Pornic"
        print(f"\n--- 🌍 TEST 2 : RECHERCHE LIVE ({ville}) ---")
        req = restaurant_pb2.CityRequest(city=ville)
        
        response = stub.GetRestaurantByCity(req)
        print(f"L'API a répondu avec {len(response.restaurants)} restaurants à {ville}.")
        
        for r in response.restaurants[:3]:
            print(f"- {r.name} ({r.city})")

        # TEST 3 : Recherche dans le nom
        nomResto = "LE PACÔME LES AUTRES"
        print(f"\n--- 🔎 TEST 3 : RECHERCHE PAR NOM ({nomResto}) ---")
        req = restaurant_pb2.NameRequest(name=nomResto)
        response = stub.GetRestaurantByName(req)
        print(f"Recherche du nom '{nomResto}' a renvoyé {len(response.restaurants)} résultats.")
        for r in response.restaurants[:3]:
            print(f"- {r.name} ({r.city})")


if __name__ == '__main__':
    run()