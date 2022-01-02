from flask import Flask, jsonify

import calibre
import digikam
import gimp
import libreoffice
import mozilla
import osmand
import transmission
import ubuntu
import inkscape
from utils import get_all_programs

app = Flask(__name__)

app.config['ENV'] = 'development'


@app.route("/")
def index():
    return jsonify(get_all_programs())


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


@app.route("/libreoffice/<program>")
def libreoffice_route(program):
    r = libreoffice.get(program)
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/mozilla/<program>")
def mozilla_route(program):
    r = mozilla.get(program)
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/digikam")
def digikam_route():
    r = digikam.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


@app.route("/transmission")
def transmission_route():
    r = transmission.get()
    if r is not None:
        return jsonify(r)
    else:
        return "NoData", 404


app.run(host="0.0.0.0")
