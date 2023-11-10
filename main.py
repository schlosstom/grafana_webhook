#!/usr/bin/python3

"""
------------------------------------------------------------------------------
Copyright (c) 2023 SUSE LLC

This program is free software; you can redistribute it and/or modify it under
the terms of version 3 of the GNU General Public License as published by the
Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, contact SUSE Linux GmbH.

------------------------------------------------------------------------------
Author: Thomas Schlosser <thomas.schlosser@suse.com>

A simple webhook client which is receiving webhook alert from prometheus alertmanager.

The following lines are needed in the alertmanager.yaml file:

receivers:
  - name: 'webhook'
    webhook_configs:
    - url: 'http://<ip_where_this_code_is_running>:8080/webhook'
      send_resolved: true

To see the alert open the following page in you browser:

http://<ip_where_this_code_is_running>:8080/webhook

Changelog:  2023-11-08  v0.1 Implementing the first basic functionalities
            2023-11-09  v0.2 Add different colors for firing and resolved

"""

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create a db table with all needed variables and labels
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime(), default=datetime.now())
    status = db.Column(db.String(20), nullable=True)
    instance = db.Column(db.String(100), nullable=True)
    job = db.Column(db.String(100), nullable=True)
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.String(300), nullable=True)
    fingerprint = db.Column(db.String(30), nullable=True)
    alertname = db.Column(db.String(30), nullable=True)
    monitor = db.Column(db.String(30), nullable=True) 
    name = db.Column(db.String(30), nullable=True) 



@app.route("/webhook", methods=['GET','POST'])
def webhook():
    if request.method == 'POST':                
        dict = request.json              
        new_message = Message(
            created_at = datetime.now(),
            start = dict['alerts'][0]['startsAt'], 
            status = dict['status'],
            instance = dict['alerts'][0]['labels']['instance'],
            alertname = dict['alerts'][0]['labels']['alertname'],
            monitor = dict['alerts'][0]['labels']['monitor'],
            job = dict['alerts'][0]['labels']['job'],
            title = dict['alerts'][0]['annotations']['title'],
            description = dict['alerts'][0]['annotations']['description'], 
            fingerprint = dict['alerts'][0]['fingerprint']
        )

        db.session.add(new_message)
        
        # If message count equal or more then 20 delete the olderst alert 
        if db.session.query(Message).count() >= 20:   
            query = db.session.query(Message)
            for item in query.order_by(Message.id).limit(1).all():
                query.filter(Message.id == item.id).delete()

        # Commit everything to the db.
        db.session.commit()
    
    # Order messages that the newest alert is on top of the page.                  
    messages = Message.query.order_by(Message.created_at).all()    
    
    return render_template("index.html", messages=messages)


# Site for deleting the entries of the db.
# redirect back if done.
@app.route("/delete", methods=['GET'])
def delete():
    db.drop_all()
    db.create_all()
    return redirect(url_for('webhook'))  


# Main routine
if __name__ == "__main__":
    db.create_all()
    app.run(host='0.0.0.0',port=8080,debug=True)
    


