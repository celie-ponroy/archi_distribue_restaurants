from difflib import SequenceMatcher
import grpc
from concurrent import futures
import requests
import restaurant_pb2
import restaurant_pb2_grpc

# --- 1. CONFIGURATION ---
# URL pour charger le cache (les 50 premiers "au pif")
API_URL_ALL = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire&rows=50"

# URL de base pour la recherche (on ajoutera &q=Ville à la fin)
API_URL_SEARCH = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire&rows=10000"

# --- 2. NOTRE CACHE (RAM) ---
# Plus de Mongo ! Juste une liste Python.
CACHE_RESTAURANTS = []

def parse_opendata_to_grpc(record_list):
    """Petite fonction pour convertir le JSON moche en objets propres"""
    cleaned_list = []
    for item in record_list:
        fields = item.get("fields", {})
        cleaned_list.append(restaurant_pb2.Restaurant(
            name=fields.get("nomoffre", fields.get("nom_etablissement", "Inconnu")),
            address=fields.get("adresse1", "") + " " + fields.get("adresse2", "") + " " + fields.get("adresse3", ""),
            city=fields.get("commune", ""),
            type=fields.get("type_offre", "Restaurant")
        ))
    return cleaned_list

def init_cache():
    """Appelé au démarrage : remplit la variable CACHE_RESTAURANTS"""
    print("🔄 Remplissage du cache (RAM) depuis l'API...")
    global CACHE_RESTAURANTS
    try:
        response = requests.get(API_URL_ALL)
        data = response.json()
        # On convertit et on stocke dans la variable globale
        CACHE_RESTAURANTS = parse_opendata_to_grpc(data.get("records", []))
        print(f"✅ Cache rempli avec {len(CACHE_RESTAURANTS)} restaurants en mémoire.")
    except Exception as e:
        print(f"❌ Erreur cache: {e}")

class RestaurantService(restaurant_pb2_grpc.RestaurantServiceServicer):
    
    # CAS 1 : On lit le Cache (Super rapide)
    def GetAllRestaurants(self, request, context):
        print(f"📥 GetAll : Je sers {len(CACHE_RESTAURANTS)} restos depuis la RAM.")
        return restaurant_pb2.RestaurantList(restaurants=CACHE_RESTAURANTS)

    # CAS 2 : On tape l'API en direct (Recherche live)
    def GetRestaurantByCity(self, request, context):
        ville = request.city
        print(f"🌍 GetByCity : Je cherche '{ville}' sur l'API externe...")
        
        # On construit l'URL avec le filtre
        # q=Nantes permet de chercher "Nantes" dans le texte
        url_live = f"{API_URL_SEARCH}&q={ville}"
        
        try:
            resp = requests.get(url_live)
            data = resp.json()
            
            # On convertit le JSON reçu
            live_results = parse_opendata_to_grpc(data.get("records", []))
            
            print(f"-> Trouvé {len(live_results)} résultats en ligne.")
            return restaurant_pb2.RestaurantList(restaurants=live_results)
            
        except Exception as e:
            print(f"Erreur API: {e}")
            return restaurant_pb2.RestaurantList()
        
    def GetRestaurantByName(self, request, context):
        nom_cherche = request.name.lower()
        print(f"🔎 Recherche floue pour : '{request.name}'...")

        # ÉTAPE 1 : On regarde dans le CACHE (RAM)
        resultats_cache = []
        
        for r in CACHE_RESTAURANTS:
            nom_resto = r.name.lower()
            
            score = SequenceMatcher(None, nom_cherche, nom_resto).ratio()
            
            if (nom_cherche in nom_resto) or (score > 0.6):
                resultats_cache.append(r)

        if len(resultats_cache) > 0:
            print(f"   -> Trouvé {len(resultats_cache)} dans le CACHE (similaire).")
            return restaurant_pb2.RestaurantList(restaurants=resultats_cache)
        
        print("   -> Pas trouvé en cache. Interrogation de l'API...")
        try:
            url_live = f"{API_URL_SEARCH}q={request.name}"
            resp = requests.get(url_live)
            data = resp.json()
            
            api_results = parse_opendata_to_grpc(data.get("records", []))
            print(f"   -> L'API a renvoyé {len(api_results)} résultats.")
            
            return restaurant_pb2.RestaurantList(restaurants=api_results)

        except Exception as e:
            print(f"❌ Erreur API: {e}")
            return restaurant_pb2.RestaurantList()

def serve():
    init_cache() # <-- On remplit la mémoire AVANT de lancer le serveur
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServiceServicer_to_server(RestaurantService(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 Serveur Hybride prêt sur le port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()