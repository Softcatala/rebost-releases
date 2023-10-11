from flask import Flask, jsonify

import calibre
import debian
import fedora
import notepadplusplus
import opensuse
import sevenzip
import tor
from kde import digikam, krita, kdenlive, gcompris
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
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/inkscape")
def inkscape_route():
    r = inkscape.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/gimp")
def gimp_route():
    r = gimp.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/calibre")
def calibre_route():
    r = calibre.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/osmand")
def osmand_route():
    r = osmand.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/libreoffice/<program>")
def libreoffice_route(program):
    r = libreoffice.get(program)
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/mozilla/<program>")
def mozilla_route(program):
    r = mozilla.get(program)
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/digikam")
def digikam_route():
    r = digikam.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/krita")
def krita_route():
    r = krita.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/kdenlive")
def kdenlive_route():
    r = kdenlive.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404

@app.route("/gcompris")
def gcompris_route():
    r = gcompris.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/transmission")
def transmission_route():
    r = transmission.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/tor")
def tor_route():
    r = tor.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/notepadplusplus")
def notepadplusplus_route():
    r = notepadplusplus.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/7zip")
def sevenzip_route():
    r = sevenzip.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/debian")
def debian_route():
    r = debian.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404



@app.route("/fedora")
def fedora_route():
    r = fedora.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


@app.route("/opensuse")
def opensuse_route():
    r = opensuse.get()
    if r is not None:
        return __jsonify(r)
    else:
        return "NoData", 404


def __jsonify(r):
    r = sorted(r, key=lambda x: x['download_os'], reverse=True)
    return jsonify(r)


app.run(host="0.0.0.0")
