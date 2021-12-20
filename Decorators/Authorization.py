from flask import abort, request, redirect, jsonify
from functools import wraps
from PrivateClasses.Token import Token


def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        users = Token()

        if 'Authorization' not in request.headers:
            if '/api' in request.path:
                return jsonify({'status': False, 'message': '401 Unauthorized'})
            else:
                return redirect('/login')

        data = request.headers['Authorization'].encode('ascii','ignore')
        token = data.decode('utf-8')
        try:
            user = users.verify_auth_token(token)
            if user is None:
                if 'api' in request.path:
                    abort(401)
                else:
                    return redirect('/login')
        except Exception as error:
            print('Token auth error: {error}'.format(error=error), flush=True)
            if 'api' in request.path:
                abort(401)
            else:
                return redirect('/login')

        return f(*args, **kwargs)
    return decorated_function
