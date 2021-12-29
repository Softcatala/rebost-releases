from flask import Flask
import json
import ubuntu

app = Flask(__name__)

app.config['ENV'] = 'development'


@app.route("/ubuntu/<flavor>")
def ubuntu_route(flavor):
    r = ubuntu.get(flavor)
    if r is not None:
        return json.dumps(r, indent=4)
    else:
        return "NoData", 404


app.run(host="0.0.0.0")
