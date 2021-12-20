from . import routes
from flask import request, jsonify, session
from Decorators.Authorization import authorize
from PrivateClasses.Database import Database
import Configuration


@routes.route('/api/rescan_tuya_devices', methods=['GET'])
def api_scan_tuya_devices():
    tuya = Configuration.global_parameters['tuya']
    devices = tuya.scan_devices()
    return jsonify({'status': True, 'result': 'Tuya device scan completed: {num} devices found.'.format(num=len(devices))})


@authorize
@routes.route('/api/set_tuya_devices', methods=['POST', 'PATCH'])
def api_set_tuya_devices():
    data = request.json
    database = Database()
    with database:
        result = database.set_tuya_devices(data)
        return jsonify({'status': True, 'result': result})


@authorize
@routes.route('/api/get_tuya_devices', methods=['GET'])
def api_get_tuya_devices():
    database = Database()
    with database:
        result = database.get_tuya_devices()
        return jsonify({'status': True, 'result': {x['_id']: x for x in result}})
