from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
from flask import Flask, request, jsonify,make_response
import resolvers as r

type_defs = load_schema_from_path("avis/avis.graphql")
query = QueryType()
mutation = MutationType()
avis = ObjectType("Avis")

query.set_field("getAllAvis", r.get_all_avis)
query.set_field("getAvisById", r.get_avis_by_id)
query.set_field("getAvisByRestaurant", r.get_avis_by_restaurant)
query.set_field("getAvisByUser", r.get_avis_by_user)
query.set_field("getAvisByRating", r.get_avis_by_rating)

mutation.set_field("updateAvis", r.update_avis)
mutation.set_field("createAvis", r.create_avis)
mutation.set_field("deleteAvis", r.delete_avis)

schema = make_executable_schema(type_defs, query, mutation, avis)

PORT = 3200
HOST = '0.0.0.0'
app = Flask(__name__)

@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# graphql entry points
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
                        schema,
                        data,
                        context_value=None,
                        debug=app.debug
                    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)