from flask import request, jsonify, session
from . import routes
from Decorators.Authorization import authorize
from PrivateClasses.UserManagement import UserManagement


@authorize
@routes.route('/api/user/add', methods=['POST'])
def api_users_add():
    """
        ---
        tags:
           - User management
        post:
          summary: User management, add user
          description: add user
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
                  admin:
                    type: boolean
                    example: true
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
    data = request.json
    session_user = session['username']
    result = UserManagement().add(session_user=session_user,
                                  username=data['username'],
                                  admin=data['admin'],
                                  clear_password=data['password'])
    return jsonify(result)


@authorize
@routes.route('/api/user/delete', methods=['DELETE'])
def api_users_del():
    """
        ---
        tags:
           - User management
        delete:
          summary: User management, delete user
          description: delete user
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
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    data = request.json
    session_user = session['username']
    result = UserManagement().delete(session_user=session_user,
                                     username=data['username'])
    return jsonify(result)


@authorize
@routes.route('/api/user/password', methods=['POST'])
def api_users_password():
    """
        ---
        tags:
           - User management
        post:
          summary: User management, change password
          description: change password
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
                  new_password:
                    type: string
                    example: secret
                  new_password_verify:
                    type: string
                    example: secret
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    data = request.json
    min_length = 5
    new_password = data['new_password']
    new_password_verify = data['new_password_verify']

    if len(new_password) < min_length:
        return jsonify({'status': False,
                        'message': 'new password must be at least {min_length} characters long'.format(min_length=min_length)}), 400

    if new_password != new_password_verify:
        return jsonify({'status': False, 'message': 'passwords don\'t match'}), 400

    session_user = session['username']
    result = UserManagement().password(session_user=session_user,
                                       clear_password=data['new_password'])
    return jsonify(result)


@authorize
@routes.route('/api/user/admin', methods=['POST'])
def api_users_admin():
    """
        ---
        tags:
           - User management
        post:
          summary: User management, set admin
          description: (un)-set admin rights
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
                  admin:
                    type: boolean
                    example: true
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    data = request.json
    session_user = session['username']
    result = UserManagement().admin_rights(session_user=session_user,
                                           username=data['username'],
                                           admin=data['admin'])
    return jsonify(result)


@authorize
@routes.route('/api/user/query', methods=['GET'])
def api_user_query():
    """
        ---
        tags:
           - User management
        get:
          summary: User management, query single user
          description: query single user
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
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    data = request.json
    result = UserManagement().list_user(username=data['username'])
    return jsonify(result)


@authorize
@routes.route('/api/users/query', methods=['GET'])
def api_users_query():
    """
        ---
        tags:
           - User management
        get:
          summary: User management, query all users
          description: query all users
          produces:
            - application/json
        responses:
          200:
            description: application token
            content:
              application/json:
                schema:
                  type: object
    """
    result = UserManagement().list_users()
    return jsonify(result)
