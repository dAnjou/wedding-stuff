#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, redirect, request, Markup, escape, Response

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import desc
import itertools
import random
import re

app = Flask(__name__)
app.config.from_envvar('WEDDING_SETTINGS')
db = SQLAlchemy(app)

class Greet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80))
    message = db.Column(db.String(150))

    def __repr__(self):
        return '<Greet %r %r>' % (self.author, self.message[:5])

@app.template_filter()
def nl2br(value):
    return Markup('<br />'.join(escape(value).split('\n')))

@app.route('/', methods=['GET', 'POST'])
def index():
    messages = []
    if request.method == 'POST':
        author = request.form['from']
        message = request.form['message']
        if len(''.join(message.split('\n'))) > 140 or len(message.split('\n')) > 5:
            messages.append(("Deine Nachricht war leider zu lang.", 'error'))
        else:
            greet = Greet()
            greet.author = author
            greet.message = message
            db.session.add(greet)
            db.session.commit()
            messages.append(("Deine Nachricht ist angekommen! Danke.", 'success'))
    if request.user_agent.platform in ['android', 'iphone']:
        entries = Greet.query.order_by(desc(Greet.id))
        return render_template('index.html', greets=entries, mobile=True, messages=messages)
    return render_template('index.html', greets=[], mobile=False, messages=messages)

@app.route('/greets/')
def greets():
    entries = Greet.query.order_by(desc(Greet.id))
    greets = []
    if entries.first():
        last = (0, 0, 1)
        distance = 600
        greets.append({'greet': entries[0], 'x': 0, 'y': 0, 'z': 0, 'rotate': 0, 'scale': 1})
        for i, greet in enumerate(entries[1:]):
            c = (
                last[0] + random.randrange(350, distance, 50),
                last[1] + random.randrange(350, distance, 50),
                last[2] * -1
            )
            last = c
            greets.append({
                'greet': greet,
                'x': c[0],
                'y': c[1],
                'z': 0,
                'rotate': c[2] * random.randrange(15, 40, 5),
                'scale': 1
            })
    return render_template('greets.html', greets=greets)

if __name__ == '__main__':
    app.run()
