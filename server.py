#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, jsonify, redirect, request, Markup, escape, Response, send_from_directory
from werkzeug import secure_filename

from flask.ext.sqlalchemy import SQLAlchemy

from sqlalchemy import desc, asc
import itertools
import random
import re
import os

app = Flask(__name__)
app.config.from_envvar('WEDDING_SETTINGS')
db = SQLAlchemy(app)

class Greet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=True)
    message = db.Column(db.String(150), nullable=True)
    is_image = db.Column(db.Boolean)
    image = db.Column(db.String, nullable=True)

    def __init__(self, is_image=False):
        self.is_image = is_image

    def __repr__(self):
        return '<Greet %r %r>' % (self.author, self.message[:5])

@app.template_filter()
def nl2br(value):
    return Markup('<br />'.join(escape(value).split('\n')))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_FILES_DEST'], filename)

@app.route('/', methods=['GET', 'POST'])
def index():
    messages = []
    if request.method == 'POST':
        greet = Greet()
        if 'photo' in request.files:
            f = request.files['photo']
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOADED_FILES_DEST'], filename))
                greet.is_image = True
                greet.image = filename
                db.session.add(greet)
        else:
            author = request.form['from']
            message = request.form['message']
            if len(''.join(message.split('\n'))) > 140 or len(message.split('\n')) > 5:
                messages.append(("Deine Nachricht war leider zu lang.", 'error'))
            else:
                greet.author = author
                greet.message = message
                db.session.add(greet)
        db.session.commit()
        messages.append(("Deine Nachricht ist angekommen! Danke.", 'success'))
    if request.user_agent.platform in ['android', 'iphone']:
        entries = Greet.query.order_by(asc(Greet.id))
        return render_template('index.html', greets=entries, mobile=True, messages=messages)
    return render_template('index.html', greets=[], mobile=False, messages=messages)

def make_greets(entries):
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
    return greets

@app.route('/greets/')
def greets():
    entries = Greet.query.order_by(asc(Greet.id))
    greets = make_greets(entries)
    return render_template('greets.html', greets=greets)

@app.route('/latestgreets/<lastid>')
def latest_greets(lastid):
    entries = Greet.query.filter(Greet.id > lastid).order_by(asc(Greet.id))
    greets = make_greets(entries)
    return render_template('greet.html', greets=greets)

@app.route('/aretherenewgreets/', defaults={'lastid': None})
@app.route('/aretherenewgreets/<int:lastid>')
def are_there_new_greets(lastid):
    if not lastid:
        lastid = request.args.get('lastid', default=-1, type=int)
    if not lastid == -1 and Greet.query.filter(Greet.id > lastid).first():
        return "yes"
    return "no"

if __name__ == '__main__':
    app.run()
