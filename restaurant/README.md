lancer docker :
`docker compose up`

si maj proto lancer à la racine du projet :
`python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. restaurant/restaurant.proto`

lancer serveur :
`python -m restaurant.server`

lancer client :
`python -m restaurant.client`

arreter docker :
`docker compose down`