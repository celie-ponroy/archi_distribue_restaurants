
# API Avis

Les avis permettent aux utilisateurs de noter et de mettre un commentaire sur le restaurant : 

    Avis : {
    _id: ObjectId,
    id_restaurant : String,
    user : String,
    note : Float,
    commentaire :String,
    }
    

## Ajout d'un avis
**create_avis(restaurant_id: String!, user_id: String!, commentaire: String, note: Float!): Avis** : créer l'avis si le restaurant existe

## Récupération des données

**allAvis: [Avis]** : renvoi tous les avis de la base de données 

**avisByID(id_avis:String!):Avis** :  récupère un avis grâce à son ID 

**avisByRestaurant(restaurant_id: String!): [Avis]** : renvoi tous les avis d'un restaurant donné

**avisByUser(user_id: String!): [Avis]** : renvoi tous les avis d'un user donné

**averageRateByRestaurant(restaurant_id: String!): Float** : renvoi la moyenne des avis sur le restaurants donné
 
## Modification d'un avis

**update_avis(id_avis: String!, note: Float!, commentaire:String!): Avis** : Modifie la note et le commentaire de l'avis si vous en êtes l'auteur

## Suppression  d'un avis
**delete_avis(id: String!): String** : supprime l'avis si vous en êtes l'auteur ou un admin
