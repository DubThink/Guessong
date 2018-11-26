from time import time

import json
from flask import render_template, flash, redirect, url_for, abort, send_from_directory, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
import os
from app.models import User
from werkzeug.urls import url_parse
import requests
import time
ADMIN_ID = 1


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Sam'}
    return render_template('index.html', title='Home', user=user)

@app.route('/resource/<path:path>')
def serve_file(path):
    return send_from_directory('resource', path)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html')
