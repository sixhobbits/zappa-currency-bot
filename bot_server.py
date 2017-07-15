from flask import Flask
from flask import request

from currencybot import run

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def receive():
    try:
        run(request.json)
        return ""
    except Exception as e:
        print(e)
        return ""

