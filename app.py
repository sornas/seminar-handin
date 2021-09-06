from datetime import datetime
import glob
import json
import os
import random

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
            uid = fpath.split("/")[-1]
            handins.append((
                datetime.fromisoformat(content["time"]).strftime("%H:%M:%S"),
                f"/{config.TEACHER_SECRET}/handins/{uid}",
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
    return render_template("student.html", handin_received=request.args.get("handin_received"))


@app.route("/", methods=["POST"])
def recv_post():
    uid = str(random.randint(1000000000, 9999999999))
    code, name = request.form["code"], request.form["name"]
    if code == "":
        print(f"{uid}: ignoring empty input from {name}")
        return redirect(url_for("student"))
    print(f"{uid}: received code from {name}")
    time = datetime.now()
    with open("handins/" + uid, "w") as f:
        f.write(json.dumps({
            "code": code.replace("\r\n", "\n"),
            "name": name,
            "time": time.isoformat(),
        }))
    print(f"{uid}: written to file")
    return redirect(url_for("student", handin_received=time.isoformat(" ", timespec="minutes")))
