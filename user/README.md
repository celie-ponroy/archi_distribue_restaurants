# API Authentification et création d'utilisateur

## Endpoints présents

### Authentification

> localhosthttp://localhost:8080/authapi.php

#### POST

Cet endpoint est utilisé pour la récupération du token d'un utilisateur

#### GET

Cet endpoint est utilisé pour la vérification du token d'un utilisateur

### Gestion d'utilisateurs  

> localhosthttp://localhost:8080/users.php

#### POST

Cet endpoint est utilisé pour la création d'utilisateur

*Un token admin est requis pour la création d'user admin*

#### DELETE
Cet endpoint est utilisé pour la supression d'utilisateur

> ?login = **login**

*Un token admin est requis pour la suppression d'utilisateurs*

#### GET


Cet endpoint est utilisé pour récupérer tous les utilisateurs

> ?all

Cet endpoint est utilisé pour récupérer un unique utilisateur

> ?login = **login**

*Un token admin est requis pour la récupération d'utilisateurs*
