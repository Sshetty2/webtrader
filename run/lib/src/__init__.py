#!/usr/bin/env python3 

from flask import Flask

from .views.authorized import controller as authorized_controller
from .views.unauthorized import controller as unauthorized_controller

omnibus = Flask(__name__)

omnibus.register_blueprint(authorized_controller)
omnibus.register_blueprint(unauthorized_controller)
