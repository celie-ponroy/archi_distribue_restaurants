# gRPC Restaurant Service - Nantes Open Data

Ce projet est un micro-service performant basé sur **gRPC** permettant d'explorer et de filtrer l'offre touristique des restaurants de la région Pays de la Loire.

## Source des Données
Le service consomme le jeu de données officiel **"Offre touristique (en Pays de la Loire) - Restaurants"** fourni par le portail Open Data de Nantes Métropole.

[Consulter le jeu de données sur Nantes Métropole](https://data.nantesmetropole.fr/explore/dataset/234400034_070-008_offre-touristique-restaurants-rpdl%40paysdelaloire/information/)

* **Nombre d'entrées :** ~4000 restaurants.
* **Mise à jour :** Les données sont récupérées dynamiquement via l'API au lancement du serveur.

## Points Forts du Projet

* **Performance gRPC** : Communication binaire ultra-rapide et typage strict via Protobuf.
* **Smart Search** : Recherche par correspondance floue pour tolérer les fautes de frappe.
* **Normalisation** : 
    * Suppression des accents (`unidecode`).
    * Passage en minuscules.
    * Suppression des caractères spéciaux via Regex.
* **Recherche Combinée** (Logique Floue + Filtre)
* **Data Caching** : Chargement initial de ~4000 records en mémoire pour des réponses instantanées.
* **Docker Ready** : Déploiement simplifié via une image Alpine Linux optimisée.

---

## 🛠️ Architecture Technique

### Structure des fichiers

```text
.
├── restaurant.py            # Serveur gRPC (Logique métier & Data)
├── client.py                # Client de test (Audit complet)
├── restaurant.proto         # Définition des contrats de données
├── restaurant_pb2.py        # Code généré (Messages)
├── restaurant_pb2_grpc.py   # Code généré (Service)
├── requirements.txt         # Dépendances Python
└── Dockerfile               # Containerisation du service

```

### Le Contrat gRPC (`.proto`)

Le service définit plusieurs méthodes de recherche pour répondre à des besoins variés :

* `SearchByName` : Recherche textuelle floue.
* `SearchByCategorie` / `SearchByType` : Filtrage par index thématiques.
* `SearchByCapacity` : Filtres numériques (min/max couverts, salles, etc.).
* `SearchByLocation` : Recherche par CP ou Commune.

---

## 💻 Installation et Utilisation

#### 1. Installation des dépendances

Il est recommandé d'utiliser un environnement virtuel :

```bash
pip install -r requirements.txt
```

#### 2. Lancer le serveur

Le serveur récupère les données en temps réel au démarrage :

```bash
python restaurant.py
```

*Le serveur écoute par défaut sur le port **50051**.*

#### 3. Exécuter l'audit (Client)

Pour valider toutes les fonctionnalités du service :

```bash
python client.py
```

#### 4. Exécuter via docker

Possibilité de lancer directement via docker

```bash
docker-compose up --build
```