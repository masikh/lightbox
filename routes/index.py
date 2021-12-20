import Configuration
from flask import Response
from . import routes


@routes.route('/')
def index():
    cwd = Configuration.cwd
    with open('{cwd}/vue_web_code/dist/index.html'.format(cwd=cwd), 'r') as f:
        content = f.read()
        return Response(content, mimetype='text/html')


@routes.route('/favicon.ico')
def favicon():
    cwd = Configuration.cwd
    with open('{cwd}/vue_web_code/dist/favicon.ico'.format(cwd=cwd), 'rb') as f:
        content = f.read()
        return Response(content, mimetype='image/x-icon')


@routes.route('/css/<filename>')
def css_files(filename):
    cwd = Configuration.cwd
    with open('{cwd}/vue_web_code/dist/css/{filename}'.format(cwd=cwd, filename=filename), 'r') as f:
        content = f.read()
        return Response(content, mimetype='text/css')


@routes.route('/js/<filename>')
def js_files(filename):
    cwd = Configuration.cwd
    with open('{cwd}/vue_web_code/dist/js/{filename}'.format(cwd=cwd, filename=filename), 'r') as f:
        content = f.read()
        return Response(content, mimetype='text/javascript')


@routes.route('/img/<filename>')
def img_files(filename):
    cwd = Configuration.cwd
    with open('{cwd}/vue_web_code/dist/img/{filename}'.format(cwd=cwd, filename=filename), 'rb') as f:
        content = f.read()
        return content
