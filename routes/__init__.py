from flask import Blueprint
routes = Blueprint('routes', __name__)

from .authenticate import *
from .index import *
from .user_management import *
from .tuya_credentials import *
from .tuya_devices import *
from .tuya_set_color import *
from .light_groups import *
