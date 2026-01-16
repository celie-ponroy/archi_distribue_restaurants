import grpc
from concurrent import futures
import requests
import re
from unidecode import unidecode
from difflib import SequenceMatcher
from restaurant import restaurant_pb2
from restaurant import restaurant_pb2_grpc

DATASET = "234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire"
BASE_URL = f"https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire"

TYPES_MAP = {1: "Ferme auberge", 2: "Food Truck", 3: "Hôtel restaurant", 4: "Restaurant", 5: "Restaurant pour groupes exclusivement", 6: "Aucune information"}
CAT_MAP = {1: "Bistrot / bar à vin", 2: "Brasserie", 3: "Cafétéria", 4: "Coffee-shop", 5: "Crêperie", 6: "Cuisine du Monde", 7: "Cuisine traditionnelle", 8: "Fruits de mer", 9: "Grill - Rôtisserie", 10: "Guinguette", 11: "Pizzeria", 12: "Restaurant bistronomique", 13: "Restaurant gastronomique - cuisine raffinée", 14: "Restaurant troglodytique", 15: "Restauration rapide", 16: "Salon de thé", 17: "Aucune information"}

class RestaurantService(restaurant_pb2_grpc.RestaurantServiceServicer):
    def __init__(self):
        self.cache = self._load_data()

    def _normalize(self, text):
        if not text: return ""
        text = unidecode(str(text)).lower()
        return re.sub(r'[^a-z0-9]', '', text)

    def _load_data(self):
        print("📥 Chargement des données...")
        url = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire&rows=4000"
        try:
            r = requests.get(url).json()
            records = r.get("records", [])
            
            print(f"✅ Succès : {len(records)} restaurants ont été récupérés et chargés en mémoire.")
            
            return [self._map_to_proto(item) for item in records]
        except Exception as e:
            print(f"❌ Erreur lors du chargement : {e}")
            return []

    def _map_to_proto(self, item):
        f = item.get("fields", {})
        
        addr = f"{f.get('adresse1','')} {f.get('adresse2','')} {f.get('adresse3','')} {f.get('codepostal','')} {f.get('commune','')} {f.get('departement','')}"
        
        return restaurant_pb2.Restaurant(
            id=item.get("recordid", ""),
            name=f.get("nomoffre", "Inconnu"),
            type_offre=f.get("type", "Aucune information"),
            categorie=f.get("categorie", "Aucune information"),
            full_address=re.sub(' +', ' ', addr).strip(),
            code_postal=str(f.get("codepostal", "")),
            commune=f.get("commune", ""),
            departement=f.get("departement", ""),
            tel_mobile=f.get("commmob", ""),
            tel_fixe=f.get("commtel", ""),
            fax=f.get("commfax", ""),
            email=f.get("commmail", ""),
            site_web=f.get("commweb", ""),
            video_url=f.get("plateformeurl", ""),
            label_logis=f.get("labelclassementlogis", ""),
            handicap=f.get("labeltourismehandicap", ""),
            animal_accepte=f.get("animauxacceptes", "non"),
            labels=f.get("labels", ""),
            services=f.get("services", ""),
            nb_max_couverts=int(f.get("capacitenbcouverts", 0) or 0),
            nb_salles=int(f.get("capacitenbsalles", 0) or 0),
            nb_terrasse=int(f.get("capacitenbcouvertsterrasse", 0) or 0),
            nb_reunion=int(f.get("nbreunionsalle", 0) or 0),
            nb_climatisees=int(f.get("nbsalleclimatisee", 0) or 0),
            ouvert_annee=f.get("ouverturealannee", "non"),
            tarifs=f.get("tarifs", ""),
            modes_paiement=f.get("modepaiement", "")
        )
    
    def _filter_by_query(self, dataset, query):
        if not query: return dataset
        q_norm = self._normalize(query)
        results = []
        for r in dataset:
            name_norm = self._normalize(r.name)
            if q_norm in name_norm or r.id == query or SequenceMatcher(None, q_norm, name_norm).ratio() > 0.7:
                results.append(r)
        return results

    def SearchByName(self, request, context):
        results = self._filter_by_query(self.cache, request.query)
        
        if not results:
            return restaurant_pb2.RestaurantList(error_message=f"Aucun restaurant trouvé pour '{request.query}'.")
        
        return restaurant_pb2.RestaurantList(restaurants=results)

    def SearchByType(self, request, context):
        filtered = self._filter_by_query(self.cache, request.query)
        
        if request.type_index == 6:
            res = [
                r for r in filtered 
                if not r.type_offre.strip() or 
                "aucune information" in r.type_offre.lower() or 
                "inconnu" in r.type_offre.lower()
            ]
        else:
            target = self._normalize(TYPES_MAP.get(request.type_index, ""))
            res = [r for r in filtered if target in self._normalize(r.type_offre)]
            
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByCategorie(self, request, context):
        filtered = self._filter_by_query(self.cache, request.query)
        
        if request.cat_index == 17:
            res = [r for r in filtered if not r.categorie.strip() or "aucune information" in r.categorie.lower()]
        else:
            target = self._normalize(CAT_MAP.get(request.cat_index, ""))
            res = [r for r in filtered if target in self._normalize(r.categorie)]
            
        return restaurant_pb2.RestaurantList(restaurants=res)
    
    def SearchByLocation(self, request, context):
        val = request.value.lower()
        res = [r for r in self.cache if val in r.code_postal or val in r.commune.lower() or val in r.departement.lower()]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByContact(self, request, context):
        filtered = self._filter_by_query(self.cache, request.query)
        val = request.value.lower()
        attr_map = {"mobile": "tel_mobile", "fixe": "tel_fixe", "fax": "fax", "email": "email"}
        attr = attr_map.get(request.field_type, "email")
        res = [r for r in filtered if val in getattr(r, attr).lower()]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByCapacity(self, request, context):
        filtered = self._filter_by_query(self.cache, request.query)
        attr_map = {"couverts": "nb_max_couverts", "salles": "nb_salles", "terrasse": "nb_terrasse", "reunion": "nb_reunion", "clim": "nb_climatisees"}
        attr = attr_map.get(request.field_type, "nb_max_couverts")
        res = [r for r in filtered if (request.search_min and getattr(r, attr) >= request.value) or (not request.search_min and getattr(r, attr) <= request.value)]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByStatus(self, request, context):
        filtered = self._filter_by_query(self.cache, request.query)
        val = request.ouvert.lower()
        res = [r for r in filtered if val in r.ouvert_annee.lower()]
        return restaurant_pb2.RestaurantList(restaurants=res)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServiceServicer_to_server(RestaurantService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("🚀 Serveur démarré sur le port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()