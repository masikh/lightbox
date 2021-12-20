from . import routes
from flask import request, jsonify, session
from Decorators.Authorization import authorize
from PrivateClasses.Database import Database


@authorize
@routes.route('/api/get_light_groups', methods=['GET'])
def api_get_light_groups():
    database = Database()
    with database:
        result = database.get_set_light_groups()
        return jsonify({'status': True, 'result': result})


@authorize
@routes.route('/api/set_light_groups', methods=['POST'])
def api_set_light_groups():
    data = request.json
    database = Database()
    with database:
        result = database.get_set_light_groups(light_groups=data)
        return jsonify({'status': True, 'result': result})
