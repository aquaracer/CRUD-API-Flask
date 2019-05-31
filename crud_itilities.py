import sqlite3
import urllib
import urllib.request
import requests
import datetime


def push(push_data):
    '''Цель функции заполнить 6 строк таблицы:

 трек_номер(Id) в формате  перевозчик +номер рейса + время отправления | номер рейса  | 

  город отправления |дата и время отправления| дата и время прибытия | город прибытия 

    Track ID -перевозчик + номер рейса + время отправления
    номер рейса             - берем из входных данных
    город отправления        - берем из входных данных
    дата и время отправления - берем из входных данных
    город прибытия           - берем из входных данных
    дата и время прибытия    - берем из входных данных
    
    
      '''

    conn = sqlite3.connect("forecast_bot_database.db") # или :memory: чтобы сохранить в RAM
    cursor = conn.cursor() # подключаемся к базе
    
    parts_of_data = push_data.split('/')
       
    #table_name = 'logistic_table_2'
    #request = "SELECT rowid, * FROM {0} ORDER BY Track_ID"  # создаем запрос на список ID
    #request = request.format(table_name)
    #res = [] 
    #for row in cursor.execute(request):   # создаем массив ID
    #    res.append(row[1])    
    
    Track_ID =parts_of_data[0] + parts_of_data[1] + parts_of_data[3]   # получили данные для 1й колонки
    flight_number=parts_of_data[1] # получили данные для 2й колонки
    city_of_departure = parts_of_data[2] # получили данные для 3й колонки
    date_time_of_departure = parts_of_data[3] # получили данные для 4й колонки
    city_of_arrival = parts_of_data[4] # получили данные для 5й колонки
    time_of_arrival = parts_of_data[5] # получили данные для 6й колонки
      
    table_name = parts_of_data[0]

    new_information = [(Track_ID, flight_number, city_of_departure, date_time_of_departure, city_of_arrival, time_of_arrival)]
    new_insert = "INSERT INTO {0} VALUES (?,?,?,?,?,?)"
    new_insert = new_insert.format(table_name)
    
    cursor.executemany(new_insert, new_information) # добавляем запись в базу
    conn.commit()

    request = "SELECT rowid, * FROM {0} ORDER BY Track_ID"
    request = request.format(table_name)
    print (request)



    print("Here's a listing of all the records in Table " + table_name)
    for row in cursor.execute(request):
        print(row)
    

    print('Track_ID: ', Track_ID)


    report = 'данные о полете приняты. Чтобы продолжить нажмите /Start'
    return report


def get_weather_from_yandex(date_time, city_name):
    """Функция получает погоду для конретного города в конкретное время.
       Также кеширует JSON с погодой на 7 дней для заданного города"""
    

    cur_url = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey=a3d86791-9f7c-483b-bd99-6fa3393d63d5&geocode={0}' # создаем ссылку на запрос координат города
    cur_url = cur_url.format(city_name)  # подставляем нужный город

    r = requests.get(url=cur_url) # через API запрос получаем словарь в формате JSON
    #print('список получили')
    data = r.json()
    #print(data)
    data = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'] # находим строку с долготой и широтой
    print(data)
    data=data.split(' ')
    lat= data[1] # записываем широту
    lon = data[0] # записываем долготу
    print(lat)
    print(lon)
    
    
    
    cur_url ='https://api.weather.yandex.ru/v1/forecast?lat={0}&lon={1}' # создаем ссылку на запрос погоды
    cur_url = cur_url.format(lat,lon) # подставляем долготу и широту заданного города
    header = {'X-Yandex-API-Key': '9986e832-3934-4bbd-aef1-21d632411afa'}
    r = requests.get(url=cur_url, headers=header ) # через API запрос получаем словарь в формате JSON
    print('погоду получили')
    data = r.json()
    print(data)
    add_data_to_cache(city_name, str(data)) # добавляем в КЕШ город и JSON с погодой
    

    aim_date = date_time[:10]
    aim_time = date_time[11:13]
    print (aim_time)
    
    temp_array_1 = data['forecasts'] # вытаскиваем массив словарей из JSON
    count_1 = 0
    for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
        if element['date'] == aim_date:
            index_1 = count_1
            break
        else:
            count_1 +=1
    
    aim_weather =  data['forecasts'][count_1]['hours'][int(aim_time)]           
    print(aim_weather)
    return aim_weather


def add_data_to_cache(city, JSON):
    conn = sqlite3.connect("forecast_bot_database.db") # подключаемся к базе
    cursor = conn.cursor()
    conn.commit()

    date_time_of_creation = str(datetime.datetime.now()) # получили данные для 3го столбца
    date_time_of_creation = date_time_of_creation[:19]
    id_1 = city + date_time_of_creation # получили данные для 1го столбца

    new_data = [(id_1, city, date_time_of_creation, JSON)]

    cursor.executemany("INSERT INTO Cache VALUES(?,?,?,?)", new_data) # добавляем запись в базу
    conn.commit()
    print ('данные добавлены в КЕШ')
    print("Here's a listing of all the records in the Cache:")
    for row in cursor.execute("SELECT rowid, * FROM Cache ORDER BY ID"):
        print(row)
    
    
    

time_of_arrival = '2019-06-01 00:40'
city_of_arrival = 'Toronto'


get_weather_from_yandex(time_of_arrival, city_of_arrival)

#test_data = 'C_3/121/Chicago/2019-05-30 19:40/Los Angeles/2019-05-30 21:00'
#push(test_data)

#def request_forecast(r_f_data):
    
    


#def check_in_cache(city, time_date):

 #   request = "SELECT rowid, * FROM Cache ORDER BY city"  # создаем запрос на список ID
 #   request = request.format(table_name)
 #   res = [] 
 #   for row in cursor.execute(request):   # создаем массив ID
 #       res.append(row[1])
 #   
 #   if city not in res:
 #       flag = False
 #       json_report = False
 #   else:
        
        

