#!flask/bin/python
from flask import Flask, jsonify
import sqlite3
import urllib
import urllib.request
import requests
import datetime
import crud_utilities

app = Flask(__name__)


@app.route('/todo/api/v1.0/push/<name>/<number>/<cityA>/<timeA>/<cityB>/<timeB>', methods=['GET'])
def push_app(name, number, cityA, timeA, cityB, timeB):
    """функция добавляет запись в базу. после добавления сообщает, что запись успешно добавлена"""
    report = crud_utilities.push(name, number, cityA, timeA, cityB, timeB)
    return jsonify({'tasks': report})
    
@app.route('/todo/api/v1.0/pop/<name>/<number>', methods=['GET'])
def pop_app(name, number):
    """функция удаляет запись из базы и выводит собщение об удалении.
       если такой записи нет - выводит соответствующее сообщение"""
    report = crud_utilities.pop(name, number)
    return jsonify({'tasks': report})

@app.route('/todo/api/v1.0/tasks/gw/<date_time>/<city_name>', methods=['GET'])
def get_weather_app(date_time, city_name):
    weather = crud_utilities.get_weather_from_yandex(date_time, city_name) 
    return jsonify({'tasks': weather})

@app.route('/todo/api/v1.0/tasks/get_forecast/<name>/<number>', methods=['GET'])
def get_forecast_app(name, number):
    weather_1, weather_2 = crud_utilities.get_forecast(name, number) 
    return jsonify({'forecast for city of departure': weather_1}, {'forecast for city of arrival': weather_2})


@app.route('/todo/api/v1.0/hello', methods=['GET'])
def hello():   
    #b = str(username1)
    #c = b + str(username2)
    return jsonify({'tasks': 'hello'})

if __name__ == '__main__':
    app.run(debug=True)
