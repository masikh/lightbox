from . import routes
from flask import request, jsonify, session
from Decorators.Authorization import authorize
from PrivateClasses.Database import Database


@authorize
@routes.route('/api/set_tuya_credentials', methods=['POST', 'PATCH'])
def api_set_tuya_credentials():
    data = request.json
    database = Database()
    with database:
        result = database.set_tuya_credentials(data)
        return jsonify({'status': True, 'result': result})


@authorize
@routes.route('/api/get_tuya_credentials', methods=['GET'])
def api_get_tuya_credentials():
    database = Database()
    with database:
        result = database.get_tuya_credentials()
        return jsonify({'status': True, 'result': result})
