# API Authentification et création d'utilisateur

## Endpoints présents

### Authentification

> http://localhost:8080/authapi.php

#### POST - Connexion (récupérer token)

Cet endpoint est utilisé pour la récupération du token d'un utilisateur

**Body:**
```json
{
  "login": "string",
  "mdp": "string"
}
```

**Réponse:**
```json
{
  "status": 200,
  "message": "OK",
  "data": {
        "token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### GET - Vérifier token valide

Cet endpoint est utilisé pour la vérification du token d'un utilisateur

**Headers requis:**
```
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "status": 200,
  "message": "Token valide."
}
```

#### GET - Vérifier correspondance token/login

> ?verify_login=true&login=**login**

Cet endpoint est utilisé pour savoir si le token envoyé par l'utilisateur est celui de l'utilisateur précisé dans l'URL

**Headers requis:**
```
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "status": 200,
  "message": "OK",
  "data": {
    "matches": true
  }
}
```

#### GET - Vérifier statut admin

> ?check_admin=true&login=**login**

Cet endpoint est utilisé pour savoir si le token envoyé par l'utilisateur correspond à un utilisateur admin

**Headers requis:**
```
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "status": 200,
  "message": "OK",
  "data": {
    "is_admin": false
  }
}
```

### Gestion d'utilisateurs  

> http://localhost:8080/users.php

#### POST - Créer un utilisateur

Cet endpoint est utilisé pour la création d'utilisateur

**Pour créer un user admin:** Un token admin est requis

**Headers (optionnel, requis si admin):**
```
Authorization: Bearer <token>
```

**Body:**
```json
{
  "login": "string",
  "mdp": "string",
  "admin": false
}
```

**Réponse:**
```json
{
  "status": 201,
  "message": "Utilisateur créé avec succès"
}
```

#### GET - Récupérer utilisateurs

**Un token admin est requis pour toute récupération d'utilisateurs**

**Headers requis:**
```
Authorization: Bearer <token>
```

##### Récupérer tous les utilisateurs

> ?all

**Réponse:**
```json
{
  "status": 200,
  "message": "OK",
  "data": [
    {
      "login": "user1",
      "admin": false
    },
    {
      "login": "admin1",
      "admin": true
    }
  ]
}
```

##### Récupérer un utilisateur spécifique

> ?login=**login**

*Un admin peut récupérer n'importe quel utilisateur. Un utilisateur normal peut uniquement récupérer son propre compte.*

**Réponse:**
```json
{
  "status": 200,
  "message": "OK",
  "data": {
    "login": "user1",
    "admin": false
  }
}
```

#### DELETE - Supprimer un utilisateur

> ?login=**login**

Cet endpoint est utilisé pour la suppression d'utilisateur

**Un token admin est requis pour la suppression d'utilisateurs**

**Un utilisateur peut se supprimer lui-même**

**Headers requis:**
```
Authorization: Bearer <token>
```

**Réponse:**
```json
{
  "status": 200,
  "message": "Utilisateur supprimé"
}
```
