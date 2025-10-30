from flask import Flask, request, redirect, url_for, render_template, session #type: ignore
from flask_login import login_user, UserMixin, LoginManager, login_required, logout_user, current_user #type: ignore
import bcrypt
import json
from decimal import Decimal
import mysql.connector
from datetime import datetime, timedelta, date
import re
import random

app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')

#Don't use this kind of key for actual secure use, for sample purposes only
app.config['SECRET_KEY'] = 'some_derp_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'