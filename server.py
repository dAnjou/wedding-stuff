from flask import Flask, render_template, jsonify, redirect, request, g

from disqusapi import DisqusAPI

import itertools
import random
import re

# configuration
DATABASE = 'wedding.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
secret_key = 'hmd9j30tyKfNZ5724TEQ4NZnYs1IzwtYS82kiAeIPcUjNdfsGElrBnlH5BxvAnY7'
public_key = 'syFlngUecmMpaYYie6mXmFoXATUkeIwx1hqcvHirsAM5n48s5ajZCsivbRz2xQZR'
disqus = DisqusAPI(secret_key, public_key)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/greets/")
def greets():
    entries = [dict(author=result["author"]["name"], message=result["raw_message"]) for result in disqus.posts.list(forum="danjou-de")]
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
    app.run()
