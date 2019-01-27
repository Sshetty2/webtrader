#!/usr/bin/env python3 

from flask import Blueprint,render_template,request

controller = Blueprint('unauthorized', __name__)

@controller.route('/')
def home():
    return render_template('unauthorized/index.html')

