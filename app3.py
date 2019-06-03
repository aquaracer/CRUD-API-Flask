#!flask/bin/python
from flask import Flask, jsonify
import sqlite3
import urllib
import urllib.request
import requests
import datetime



app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]








@app.route('/todo/api/v1.0/tasks/<username1>/<username2>', methods=['GET'])
def get_tasks(username1, username2):   
    b = str(username1)
    c = b + str(username2)
    return jsonify({'tasks': c})

if __name__ == '__main__':
    app.run(debug=True)



