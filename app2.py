#!flask/bin/python
from flask import Flask, jsonify
import sqlite3
import urllib
import urllib.request
import requests
import datetime
import crud_utilities

app = Flask(__name__)


@app.route('/todo/api/v1.0/push/<aircompany_name>/<flight_number>/<city_of_departure>/<time_of_departure>/<city_of_arrival>/<time_of_arrival>', methods=['GET'])
def push_app(aircompany_name, flight_number, city_of_departure, time_of_departure, city_of_arrival, time_of_arrival):
    """функция добавляет запись в базу. после добавления сообщает, что запись успешно добавлена"""
    report = crud_utilities.push(aircompany_name, flight_number, city_of_departure, time_of_departure, city_of_arrival, time_of_arrival)
    return jsonify({'tasks': report})
    
@app.route('/todo/api/v1.0/pop/<aircompany_name>/<flight_number>', methods=['GET'])
def pop_app(aircompany_name, flight_number):
    """функция удаляет запись из базы и выводит собщение об удалении.
       если такой записи нет - выводит соответствующее сообщение"""
    report = crud_utilities.pop(aircompany_name, flight_number)
    return jsonify({'tasks': report})


@app.route('/todo/api/v1.0/weather/<aircompany_name>/<flight_number>', methods=['GET'])
def get_forecast_app(aircompany_name, flight_number):
    """Функция возвращает JSON с прогонозом погоды для города отправления и города прибытия указанного рейса.
        Для получения данных нужно имя авиакомпании и номер рейса"""
    weather_1, weather_2 = crud_utilities.get_forecast(aircompany_name, flight_number) 
    return jsonify({'forecast for city of departure': weather_1}, {'forecast for city of arrival': weather_2})



if __name__ == '__main__':
    app.run(debug=True)
