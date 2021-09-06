import glob
import json
import os
import random
import time

from flask import Flask, redirect, render_template, request, url_for
import werkzeug

import config

app = Flask(__name__, static_folder="static", template_folder=os.path.abspath("html/templates"))


def static(path):
    with open(path, "r") as f:
        return f.read()


@app.route("/" + config.TEACHER_SECRET, methods=["GET"])
def teacher():
    handins = []
    for fpath in glob.glob("handins/*"):
        with open(fpath, "r") as f:
            content = json.load(f)
            handins.append((
                content["time"],
                request.url + "/" + fpath,
                content["name"]
            ))
    handins.sort()
    return render_template("teacher.html", handins=handins)


@app.route("/" + config.TEACHER_SECRET + "/handins/<uid>", methods=["GET"])
def teacher_show(uid):
    path = werkzeug.security.safe_join("handins", uid)
    with open(path, "r") as f:
        content = json.load(f)
        print(content["code"])
        return "<code>" + content["code"].replace("\n", "<br>").replace(" ", "&nbsp;") + "</code>"
    return "Invalid uid {}".format(uid), 400


@app.route("/", methods=["GET"])
def student():
    return static("html/student.html")


@app.route("/", methods=["POST"])
def recv_post():
    uid = random.randint(1000000000, 9999999999)
    response = redirect(url_for("student"))
    code, name = request.form["code"], request.form["name"]
    if code == "":
        print(f"{uid}: ignoring empty input from {name}")
        return response
    print(f"{uid}: received code from {name}")
    with open("handins/" + str(uid), "w") as f:
        f.write(json.dumps({
            "code": code.replace("\r\n", "\n"),
            "name": name,
            "time": time.time_ns(),
        }))
    print(f"{uid}: written to file")
    return response
