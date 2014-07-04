# -*- coding: utf-8 -*-

from flask import Flask, jsonify
from .models import Server

app = Flask(__name__)

@app.route("/")
def index():
    list = Server.getlist()
    return jsonify(serverlist=[
        {"ip": srv.ip, "port": srv.port} for srv in list
    ])
