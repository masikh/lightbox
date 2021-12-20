from . import routes
from flask import request, jsonify
from Decorators.Authorization import authorize
import Configuration
import pychromecast

@authorize
@routes.route('/api/tuya_colour_rotation_speed', methods=['POST'])
def api_tuya_colour_rotation_speed():
    tuya = Configuration.global_parameters['tuya']
    data = request.json
    if 'mood' in data and 'colour_rotation_speed' in data:
        tuya.set_colour_rotation_speed(data)
        return jsonify({'status': True, 'result': True})

@authorize
@routes.route('/api/tuya_set_color', methods=['POST'])
def api_tuya_set_color():
    tuya = Configuration.global_parameters['tuya']
    data = request.json
    if data is not None and 'identifiers' in data:
        for identifier in data['identifiers']:
            if identifier in tuya.threads:
                payload = {
                    'colour': data['colour'],
                    'brightness': data['brightness'],
                    'colourtemp': data['colourtemp'],
                    'set_colour': data['set_colour']
                }
                tuya.threads[identifier]['queue'].append(payload)
    return jsonify({'status': True, 'result': True})


@authorize
@routes.route('/api/tuya_save_mood', methods=['POST'])
def api_tuya_save_color_profile():
    data = request.json
    mood = data.get('mood', {})
    if mood != {}:
        tuya = Configuration.global_parameters['tuya']
        tuya.set_color_profile(mood)
        return jsonify({'status': True, 'result': 'Profile "{name}" save'.format(name=mood['name'])})
    jsonify({'status': False, 'result': 'No profile name provided'})


@authorize
@routes.route('/api/tuya_get_moods', methods=['GET'])
def api_tuya_get_color_profiles():
    tuya = Configuration.global_parameters['tuya']
    results = tuya.get_tuya_mood_profiles()
    for i in range(len(results)):
        results[i]['_id'] = str(results[i]['_id'])

    return jsonify({'status': True, 'result': results})


# TODO: Fix authorization from IFTTT call
@routes.route('/api/tuya_activate_mood', methods=['POST'])
def api_tuya_set_mood():
    data = request.json
    name = data.get('name', None)
    if name is not None:
        print('Mood {name} activated'.format(name=name), flush=True)
        tuya = Configuration.global_parameters['tuya']
        result = tuya.set_mood(name.lower())
        return jsonify(result)
    return jsonify({'status': False, 'result': 'Undefined mood!'})


@routes.route('/api/tuya_get_default_mood', methods=['GET'])
def api_tuya_get_default_mood():
    tuya = Configuration.global_parameters['tuya']
    result = tuya.get_set_default_mood_profile()
    return jsonify({'status': True, 'result': result})


@routes.route('/api/tuya_delete_mood', methods=['POST'])
def api_tuya_delete_mood():
    data = request.json
    name = data.get('name', None)
    if name is not None:
        tuya = Configuration.global_parameters['tuya']
        result = tuya.delete_tuya_mood_profile(name)
        return jsonify({'status': True, 'result': result})


@authorize
@routes.route('/api/tuya_get_bulb_color', methods=['POST'])
def api_tuya_get_bulb_color():
    data = request.json
    device = data.get('device', None)
    if device is not None:
        tuya = Configuration.global_parameters['tuya']
        result = tuya.get_bulb_color(device)
        return jsonify({'status': True, 'result': result})
    return jsonify({'status': False, 'result': 'No device provided'})


@routes.route('/api/tuya_get_mood_names', methods=['GET'])
def api_tuya_get_mood_names():
    tuya = Configuration.global_parameters['tuya']
    result = tuya.get_tuya_mood_profiles()
    text = 'Here are your configured moods: '
    text += ', '.join(x['name'] for x in result[:-1])
    text += ' and ' + ''.join(x['name'] for x in result[-1:])
    chromecasts = tuya.get_chromecast_device()
    if chromecasts is not None:
        cast = pychromecast.get_chromecast_from_host((chromecasts, 8009, None, None, None))
        cast.wait()
        url = 'https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=en&q={text}'.format(text=text.replace(' ', '+'))

        mc = cast.media_controller
        mc.play_media(url, 'audio/mp3')
        cast.join(timeout=0.1)
    return jsonify({'status': True, 'result': 'list'})
