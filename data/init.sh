#!/bin/bash

# Importe les données depuis db.json
mongoimport --db archiDistriRestaurants --collection user --file /docker-entrypoint-initdb.d/db.json --jsonArray
