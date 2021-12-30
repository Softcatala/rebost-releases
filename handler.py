from flask import Flask, jsonify
import json

import calibre
import gimp
import ubuntu
import inkscape

app = Flask(__name__)

app.config['ENV'] = 'development'


@app.route("/")
def index():
    return jsonify([
        {'slug': 'ubuntu', 'path': '/ubuntu/ubuntu'},
        {'slug': 'xubuntu', 'path': '/ubuntu/xubuntu'},
        {'slug': 'kubuntu', 'path': '/ubuntu/kubuntu'},
        {'slug': 'ubuntu-mate', 'path': '/ubuntu/ubuntu-mate'},
        {'slug': 'inkscape', 'path': '/inkscape'},
        {'slug': 'gimp', 'path': '/gimp'},
        {'slug': 'calibre', 'path': '/calibre'},
    ])


@app.route("/ubuntu/<flavor>")
def ubuntu_route(flavor):
    r = ubuntu.get(flavor)
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/inkscape")
def inkscape_route():
    r = inkscape.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/gimp")
def gimp_route():
    r = gimp.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/calibre")
def calibre_route():
    r = calibre.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404




app.run(host="0.0.0.0")
