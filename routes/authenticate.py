from flask import jsonify, request, session, make_response, redirect
from PrivateClasses.Token import Token
from PrivateClasses.Database import Database
from PrivateClasses.UserManagement import UserManagement
from . import routes

""" Get token for accessing any API
"""


@routes.route('/api/login', methods=['POST'])
def api_login():
    """
        ---
        tags:
           - Authentication
        post:
          summary: request token
          description: This server
          consumes:
            - application/json
          produces:
            - application/json
          parameters:
            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                  username:
                    type: string
                    example: test
                  password:
                    type: string
                    example: test
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    def error_response(error):
        payload = {'token': '', 'error': error}
        resp = make_response(jsonify(payload))
        resp.headers["Content-Type"] = "application/json"
        return resp

    if request.method == 'POST':
        try:
            data = request.json
            username = data['username']
            password = data['password']

            database = Database()
            with database:
                resp = UserManagement().list_user(username=username)
                if resp['status'] is False:
                    return error_response('Incorrect username/password')

                users = UserManagement()
                checks_out = users.check(resp['message'], password)
                if not checks_out:
                    return error_response('Incorrect username/password')

            tokens = Token(username)
            token = tokens.generate_auth_token()
            if not isinstance(token, str):
                token = token.decode('utf-8')
            session['token'] = token
            session['username'] = username
            session.modified = True
            session.new = True
            session.permanent = True
            print('login requested', flush=True)
            return jsonify({'token': token, 'admin': resp['message']['admin']})
        except Exception as error:
            return error_response(error)


@routes.route('/api/logout', methods=['GET'])
def api_logout():
    try:
        session.pop('token')
        session.pop('username')
        return jsonify({'status': True, 'mesage': 'Session popped'})
    except KeyError:
        print('Logout: {"error": "No token in session"}', flush=True)
    return jsonify({'status': False, 'message': 'Failed popping session'})