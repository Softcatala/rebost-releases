from flask import Flask, jsonify
import json

import calibre
import gimp
import osmand
import ubuntu
import inkscape

app = Flask(__name__)

app.config['ENV'] = 'development'


@app.route("/")
def index():
    return jsonify([
        {'wp': 'ubuntu', 'api': 'ubuntu/ubuntu'},
        {'wp': 'xubuntu', 'api': 'ubuntu/xubuntu'},
        {'wp': 'kubuntu', 'api': 'ubuntu/kubuntu'},
        {'wp': 'ubuntu-mate', 'api': 'ubuntu/ubuntu-mate'},
        {'wp': 'inkscape', 'api': 'inkscape'},
        {'wp': 'gimp', 'api': 'gimp'},
        {'wp': 'calibre', 'api': 'calibre'},
        {'wp': 'mapa-catala-per-a-losmand', 'api': 'osmand'},
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


@app.route("/osmand")
def osmand_route():
    r = osmand.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404




app.run(host="0.0.0.0")
