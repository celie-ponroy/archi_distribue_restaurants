#!/bin/bash

# Importe les données depuis db.json
mongoimport --db archiDistriRestaurants --collection user --file /docker-entrypoint-initdb.d/db_user.json --jsonArray
mongoimport --db archiDistriRestaurants --collection avis --file /docker-entrypoint-initdb.d/db_avis.json --jsonArray
