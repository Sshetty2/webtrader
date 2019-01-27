#!/usr/bin/env python3 

from flask import Blueprint,render_template,request

controller = Blueprint('authorized', __name__, url_prefix='/authorized')