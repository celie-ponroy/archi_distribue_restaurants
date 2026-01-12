import grpc
from concurrent import futures
import requests
import re
from unidecode import unidecode
from difflib import SequenceMatcher
from restaurant import restaurant_pb2
from restaurant import restaurant_pb2_grpc

# Mappings pour les index demandés
TYPES_MAP = {1:"Ferme auberge", 2:"Food Truck", 3:"Hôtel restaurant", 4:"Restaurant", 5:"Restaurant pour groupes exclusivement", 6:"Aucune information"}
CAT_MAP = {1:"Bistrot / bar à vin", 2:"Brasserie", 3:"Cafétéria", 4:"Coffee-shop", 5:"Crêperie", 6:"Cuisine du Monde", 7:"Cuisine traditionnelle", 8:"Fruits de mer", 9:"Grill - Rôtisserie", 10:"Guinguette", 11:"Pizzeria", 12:"Restaurant bistronomique", 13:"Restaurant gastronomique - cuisine raffinée", 14:"Restaurant troglodytique", 15:"Restauration rapide", 16:"Salon de thé", 17:"Aucune information"}

API_URL = "https://data.nantesmetropole.fr/api/records/1.0/search/?dataset=234400034_070-008_offre-touristique-restaurants-rpdl@paysdelaloire&rows=100"

class RestaurantService(restaurant_pb2_grpc.RestaurantServiceServicer):
    def __init__(self):
        self.cache = self._load_all_data()

    def _load_all_data(self):
        print("📥 Chargement des données...")
        try:
            r = requests.get(API_URL)
            records = r.json().get("records", [])
            return [self._map_to_proto(item) for item in records]
        except: return []

    def _normalize(self, text):
        if not text: return ""
        text = unidecode(text).lower()
        return re.sub(r'[^a-z0-9]', '', text)

    def _map_to_proto(self, item):
        f = item.get("fields", {})
        return restaurant_pb2.Restaurant(
            id=item.get("recordid", ""),
            name=f.get("nomoffre", f.get("nom_etablissement", "Inconnu")),
            type_offre=f.get("type_offre", "Aucune information"),
            categorie=f.get("categorie_restaurant", "Aucune information"),
            full_address=f"{f.get('adresse1','')} {f.get('adresse2','')} {f.get('adresse3','')} {f.get('codepostal','')} {f.get('commune','')} {f.get('departement','')}".strip(),
            code_postal=str(f.get("codepostal", "")),
            commune=f.get("commune", ""),
            departement=f.get("departement", ""),
            tel_mobile=f.get("telephonemobile", ""),
            tel_fixe=f.get("telephone", ""),
            fax=f.get("telecopiefax", ""),
            email=f.get("email", ""),
            site_web=f.get("siteweb", ""),
            video_url=f.get("url_video", ""),
            label_logis=f.get("label_classement_logis", ""),
            handicap=f.get("label_tourisme_handicap", ""),
            animal_accepte=f.get("animauxacceptes", ""),
            labels=f.get("labels", ""),
            services=f.get("services_proposes_sur_l_equipement", ""),
            nb_max_couverts=int(f.get("capacitenbcouverts", 0) or 0),
            nb_salles=int(f.get("nombre_salles_restaurant", 0) or 0),
            nb_terrasse=int(f.get("nombre_max_couverts_en_terrasse", 0) or 0),
            nb_reunion=int(f.get("nombre_salles_de_reunion", 0) or 0),
            nb_climatisees=int(f.get("nombre_salles_climatisees", 0) or 0),
            ouvert_annee=f.get("ouvert_toute_l_annee", ""),
            horaires=f.get("horaires_ouvertures", ""),
            tarifs=f.get("tarifs", ""),
            modes_paiement=f.get("modes_de_paiement_acceptes", "")
        )

    def _find_by_id_or_name(self, query):
        q_norm = self._normalize(query)
        results = []
        for r in self.cache:
            if r.id == query or q_norm in self._normalize(r.name) or SequenceMatcher(None, q_norm, self._normalize(r.name)).ratio() > 0.8:
                results.append(r)
        return results

    def SearchByName(self, request, context):
        res = self._find_by_id_or_name(request.query)
        if not res: return restaurant_pb2.RestaurantList(error_message="Aucun restaurant trouvé pour cette recherche.")
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByType(self, request, context):
        target = TYPES_MAP.get(request.type_index, "")
        target_norm = self._normalize(target) # On normalise le texte recherché
        # On compare les versions normalisées (sans accents, minuscules)
        res = [r for r in self.cache if target_norm in self._normalize(r.type_offre)]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByCategorie(self, request, context):
        target = CAT_MAP.get(request.cat_index, "")
        target_norm = self._normalize(target)
        res = [r for r in self.cache if target_norm in self._normalize(r.categorie)]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByLocation(self, request, context):
        val = request.value.lower()
        res = [r for r in self.cache if val in r.code_postal or val in r.commune.lower() or val in r.departement.lower()]
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByCapacity(self, request, context):
        mapping = {"couverts": "nb_max_couverts", "salles": "nb_salles", "terrasse": "nb_terrasse", "reunion": "nb_reunion", "clim": "nb_climatisees"}
        field = mapping.get(request.field_type, "nb_max_couverts")
        res = []
        for r in self.cache:
            val = getattr(r, field)
            if (request.search_min and val >= request.value) or (not request.search_min and val <= request.value):
                res.append(r)
        return restaurant_pb2.RestaurantList(restaurants=res)

    def SearchByStatus(self, request, context):
        # L'API utilise souvent 'oui' ou 'non' en minuscules
        val = request.ouvert.lower()
        res = [r for r in self.cache if val in r.ouvert_annee.lower()]
        return restaurant_pb2.RestaurantList(restaurants=res)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    restaurant_pb2_grpc.add_RestaurantServiceServicer_to_server(RestaurantService(), server)
    server.add_insecure_port('[::]:50051')
    print("🚀 Serveur démarré sur le port 50051")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()