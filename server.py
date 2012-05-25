import sqlite3

from flask import Flask, render_template, jsonify, redirect, request, g

import itertools
import random
import re

# configuration
DATABASE = 'wedding.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

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
    return render_template("index.html")

@app.route("/greets/")
def greets():
    cur = g.db.execute('select author, message from greets order by id desc')
    entries = [dict(author=row[0], message=row[1]) for row in cur.fetchall()]
    greets = []
    last = (0, 0, 0)
    distance = 1000
    for i, greet in enumerate(entries):
        c = (
            random.randrange(last[0]+500, last[0]+distance, 50),
            random.randrange(last[1]+500, last[1]+distance, 50),
            random.randrange(last[2]-90, last[2]+90, 10)
        )
        last = c
        greets.append({
            "greet": greet,
            "x": c[0],
            "y": c[1],
            "z": 0,
            "rotate": c[2],
            "scale": 1
        })
    return render_template("greets.html", greets=greets)

#@app.route("/greet/", defaults={'index': 0})
#@app.route("/greet/<int:index>")
#def greet(index):
#    if index >= len(list_of_greets):
#        index = index % len(list_of_greets)
#        return redirect("/greet/%s" % index)
#    next = (index + 1) % len(list_of_greets)
#    prev = (index - 1) % len(list_of_greets)
#    return jsonify(greet=list_of_greets[index], index=index, next=next, prev=prev)

if __name__ == "__main__":
    #sqlite3 wedding.db < schema.sql
    app.run()
