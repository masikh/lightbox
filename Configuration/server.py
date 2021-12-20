import os

db = os.getenv('DB', '127.0.0.1')

# Flask server settings
environment = {
    'database': {
        'hostname': 'mongodb://{db}:27017/'.format(db=db),
        'username': 'root',
        'password': os.getenv('MONGO_PASSWORD'),
        'db_name': 'tuya',
        'db_collections': {'users': ''}
    },
    'key': 'Gnomes are not little friends with pointy hats, hence rather different',
    'flask': {
        'ip_address': '0.0.0.0',
        'port': 7890
    }
}

# Applications working directory
cwd = os.getcwd()

# Global parameters populated in: WSGIServer.app()
global_parameters = {}
