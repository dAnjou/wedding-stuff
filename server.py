import sqlite3

from flask import Flask, render_template, jsonify, redirect, request, g

import itertools
import random
import re

app = Flask(__name__)
app.config.from_envvar('WEDDING_SETTINGS')

@app.before_request
def before_request():
    g.db = sqlite3.connect(app.config['DATABASE'])

@app.teardown_request
def teardown_request(exception):
    g.db.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        g.db.execute('insert into greets (author, message) values (?, ?)',
            [request.form['from'], request.form['message']])
        g.db.commit()
    if request.user_agent.platform in ["android", "iphone"]:
        cur = g.db.execute('select author, message from greets order by id desc')
        entries = [dict(author=row[0], message=row[1]) for row in cur.fetchall()]
        return render_template("index.html", greets=entries, mobile=True)
    return render_template("index.html", greets=[], mobile=False)

@app.route("/greets/")
def greets():
    cur = g.db.execute('select author, message from greets order by id desc')
    entries = [dict(author=row[0], message=row[1]) for row in cur.fetchall()]
    greets = []
    last = (0, 0, 1)
    distance = 600
    greets.append({"greet": entries[0], "x": 0, "y": 0, "z": 0, "rotate": 0, "scale": 1})
    for i, greet in enumerate(entries[1:]):
        c = (
            last[0] + random.randrange(350, distance, 50),
            last[1] + random.randrange(350, distance, 50),
            last[2] * -1
        )
        last = c
        greets.append({
            "greet": greet,
            "x": c[0],
            "y": c[1],
            "z": 0,
            "rotate": c[2] * random.randrange(15, 40, 5),
            "scale": 1
        })
    return render_template("greets.html", greets=greets)

if __name__ == "__main__":
    app.run()
