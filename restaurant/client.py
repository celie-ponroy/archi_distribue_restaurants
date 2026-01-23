import grpc
from restaurant import restaurant_pb2
from restaurant import restaurant_pb2_grpc

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def run_full_audit():
    # Connexion au serveur sur le port 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = restaurant_pb2_grpc.RestaurantServiceStub(channel)

        print_separator("TEST 1 : RECHERCHE NOM")
        test_queries = ["Auberge l'ocean", "auberg ocean", "Pacome", "LE ESCALE"]
        for q in test_queries:
            req = restaurant_pb2.SearchRequest(query=q)
            resp = stub.SearchByName(req)
            if resp.restaurants:
                print(f"✅ Requête '{q}' : {len(resp.restaurants)} trouvé(s). Exemple : {resp.restaurants[0].name}")
            else:
                print(f"❌ Requête '{q}' : {resp.error_message}")

        print_separator("TEST 2 : TYPE DE RESTAURANT")
        for i in range(1, 7):
            req = restaurant_pb2.TypeRequest(type_index=i)
            resp = stub.SearchByType(req)
            print(f"Type index {i} : {len(resp.restaurants)} restaurant(s) trouvé(s).")

        print_separator("TEST 3 : CATÉGORIE")
        for i in range(1, 18):
            req = restaurant_pb2.CategorieRequest(cat_index=i) 
            resp = stub.SearchByCategorie(req)
            print(f"Catégorie index {i} : {len(resp.restaurants)} restaurant(s) trouvé(s).")

        print_separator("TEST 4 : LOCALISATION")
        req_cp = restaurant_pb2.LocationRequest(value="44560")
        resp_cp = stub.SearchByLocation(req_cp)
        print(f"Restaurants au CP 44560 : {len(resp_cp.restaurants)}")
        req_commune = restaurant_pb2.LocationRequest(value="Pornic")
        resp_commune = stub.SearchByLocation(req_commune)
        print(f"Restaurants à Pornic : {len(resp_commune.restaurants)}")

        print_separator("TEST 5 : CONTACTS")
        req_mail = restaurant_pb2.ContactRequest(value="gmail.com", field_type="email")
        resp_mail = stub.SearchByContact(req_mail)
        print(f"Restaurants avec email Gmail : {len(resp_mail.restaurants)}")

        print_separator("TEST 6 : CAPACITÉS")
        req_capa = restaurant_pb2.CapacityRequest(value=50, search_min=True, field_type="couverts")
        resp_capa = stub.SearchByCapacity(req_capa)
        print(f"Restaurants avec au moins 50 couverts : {len(resp_capa.restaurants)}")
        req_salles = restaurant_pb2.CapacityRequest(value=2, search_min=False, field_type="salles")
        resp_salles = stub.SearchByCapacity(req_salles)
        print(f"Restaurants avec maximum 2 salles : {len(resp_salles.restaurants)}")

        print_separator("TEST 7 : SERVICES ET STATUT")
        req_animaux = restaurant_pb2.StatusRequest(ouvert="oui") # Test d'ouverture
        resp_animaux = stub.SearchByStatus(req_animaux)
        print(f"Restaurants ouverts toute l'année : {len(resp_animaux.restaurants)}")

        if resp_cp.restaurants:
            r = resp_cp.restaurants[0]
            print_separator("TEST 8 : DÉTAILS DU PREMIER RESTAURANT DU TEST 4")
            print(f"Nom                 : {r.name}")
            print(f"ID                  : {r.id}")
            print(f"Adresse             : {r.full_address}")
            print(f"Type                : {r.type_offre}")
            print(f"Catégorie           : {r.categorie}")
            print(f"Animaux autorisés ? : {r.animal_accepte}")
            print(f"Téléphone fixe    : {r.tel_fixe}")
            print(f"Email               : {r.email}")
            print(f"Site web            : {r.site_web}")

        print_separator("TEST 9 : RECHERCHE COMBINÉE (AUBERGE ET CUISINE TRADITIONNELLE)")
        req_comb = restaurant_pb2.CategorieRequest(cat_index=7, query="Auberge")
        resp_comb = stub.SearchByCategorie(req_comb)
        print(f"Auberges en cuisine traditionnelle : {len(resp_comb.restaurants)}")

        print_separator("TEST 10 : VÉRIFICATION SEARCH_BY_ID")
        if resp_cp.restaurants:
            id_a_tester = resp_cp.restaurants[0].id
            print(f"Tentative de récupération de l'ID : {id_a_tester}")
            
            # Appel de la méthode spécifique
            req_id = restaurant_pb2.IdRequest(id=id_a_tester)
            resp_id = stub.SearchById(req_id)
            
            if resp_id.restaurants:
                r_final = resp_id.restaurants[0]
                print(f"✅ Succès ! Restaurant récupéré par ID : {r_final.name}")
            else:
                print(f"❌ Échec : {resp_id.error_message}")

if __name__ == '__main__':
    try:
        run_full_audit()
    except grpc.RpcError as e:
        print(f"❌ Erreur RPC : {e.code()} - {e.details()}")