import sqlite3
import urllib
import urllib.request
import requests
import datetime
import json

def push(name, number, cityA, timeA, cityB, timeB):
    '''Цель функции заполнить 6 строк таблицы:

 трек_номер(Id) в формате  перевозчик +номер рейса | номер рейса  | 

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
    
    Track_ID =name + number   # получили данные для 1й колонки
    flight_number=number # получили данные для 2й колонки
    city_of_departure = cityA # получили данные для 3й колонки
    date_time_of_departure = timeA # получили данные для 4й колонки
    city_of_arrival = cityB # получили данные для 5й колонки
    time_of_arrival = timeB # получили данные для 6й колонки

    new_information = [(Track_ID, flight_number, city_of_departure, date_time_of_departure, city_of_arrival, time_of_arrival)]
    new_insert = "INSERT INTO M_Flights VALUES (?,?,?,?,?,?)"
    
    
    cursor.executemany(new_insert, new_information) # добавляем запись в базу
    conn.commit()

    report = ' information has been added to the base' # формулируем сообщение об успешном добавлении записи в базу
    return report


def pop(name, number):
    ''' Функция удаляет запись из базы полетов. Входные данные название авиакомпании и номер рейса.
    Производится поиск в базе по ключу (название компании + номер рейса). Если запись найдена то происходит ее
    удаление и возвращается подтверждение об удалении.
    Если запись в базе отствует выводится соответствующее сообщение'''
         
    conn = sqlite3.connect("forecast_bot_database.db")
    cursor = conn.cursor() # подключаемся к базе
    conn.commit()

    res = [] # создаем пустой массив для результатов

    Track_ID =name+number # создаем Track_Id состоящий из имени компании и номера рейса

    for row in cursor.execute("SELECT rowid, * from M_Flights ORDER BY Track_ID"): # создаем массив записей Track_ID
        res.append(row[1])
    if Track_ID in res:  # если Track_ID есть в базе - удаляем
        c = '"' + Track_ID + '"'   # создаем кавычки для ID
        sql = "DELETE FROM M_Flights WHERE Track_ID = {0} " # формулируем запрос на удаление
        sql = sql.format(c)  # форматируем запрос
        cursor.execute(sql)  # выполняем удаление
        conn.commit()
        report = 'database entry has been deleted'
    else:
        report = 'database does not contain this record'
    return report
    

def get_weather_from_yandex(date_time, city_name):
    """Функция получает погоду для конретного города в конкретное время.
       Также кеширует JSON с погодой на 7 дней для заданного города"""
    
    cur_url = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey=a3d86791-9f7c-483b-bd99-6fa3393d63d5&geocode={0}' # создаем ссылку на запрос координат города
    cur_url = cur_url.format(city_name)  # подставляем нужный город
    r = requests.get(url=cur_url) # через API запрос получаем словарь в формате JSON
    data = r.json()
    data = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'] # находим строку с долготой и широтой
    data=data.split(' ')
    lat= data[1] # записываем широту
    lon = data[0] # записываем долготу
      
    cur_url ='https://api.weather.yandex.ru/v1/forecast?lat={0}&lon={1}' # создаем ссылку на запрос погоды
    cur_url = cur_url.format(lat,lon) # подставляем долготу и широту заданного города
    header = {'X-Yandex-API-Key': '9986e832-3934-4bbd-aef1-21d632411afa'}
    r = requests.get(url=cur_url, headers=header ) # через API запрос получаем словарь в формате JSON
    data = r.json()
    add_data_to_cache(city_name, str(data)) # добавляем в КЕШ город и JSON с погодой
    aim_date = date_time[:10]              # создаем целевую дату(дату рейса) для поиска в JSON
    aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
    aim_time = date_time[11:13]            # создаем целевое время(время рейса) для поиска в JSON 
    
    temp_array_1 = data['forecasts'] # вытаскиваем массив словарей из JSON
    count_1 = 0
    for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
        if element['date'] == aim_date:
            index_1 = count_1
            break
        else:
            count_1 +=1
    
    aim_weather =  data['forecasts'][count_1]['hours'][int(aim_time)]  # вытаскиваем прогноз погоды в заданные дату и время         
    return aim_weather


def add_data_to_cache(city, JSON):
    """Функция кеширования. В базу данных cache добавляются следующие данные по столбцам:

 ID (в формате: город + дата создания)| город | дата создания | JSON с погодой на неделю """

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
    
       
def check_in_cache(city):
    """Функция проверяет наличие JSON с погодой в кеше по заданному городу и в случае обнаружения
       актуальных данных возвращается JSON с погодой. 
       Проверка проводится в 2 этапа:
       1 этап Производится поиск заданного города в КЕШе. Если город не
       найден функция прекрщает действие. Если город найден переходим к следующему этапу - проверки актуальности данных.
       2 этап проверяем сколько прошло времени с момента создания записи в кеше до актуального запроса.
       Если с момента создания крайней записи в КЕШе до запроса прошло менее 12 часов - то берем запись из КЕШа.
       В противном случае - через другую функцию берем актуальные данные с Яндекс.Погоды"""
    
    conn = sqlite3.connect("forecast_bot_database.db") # открываем базу
    cursor = conn.cursor()
    conn.commit()
    res = [] # создаем пустой массив для результатов
    temp_city = '"' + city + '"'   # создаем кавычки для city
    sql = "SELECT date_time_of_creation FROM Cache WHERE city={0}" # ищем записи с заданным названием города
    sql=sql.format(temp_city)
    cursor.execute(sql)
    ans = cursor.fetchall() # найденные записи заносим в массив
    print(len(ans))    # выводим длину массива. 

    if len(ans) < 1:# если в массиве ничего нет - значит города нет в КЕШе и получить JSON из КЕШа не получится
        print('города нет в КЭШе')
        flag = False
        arr = False
        return flag, arr
    else:     # в противном случае в КЕШе есть как минимум одна запись для данного города
        cache_time_date = max(ans) # получили время введения в КЕШ самых актуальных данных
        cache_time_date = cache_time_date[0]
        print (cache_time_date)
        
        actual_time_date = str(datetime.datetime.now()) 
        actual_time_date = actual_time_date[:19]# получаем актуальное время
        actual_year = int(actual_time_date[:4]) # получаем актуальный год в формате ИНТ
        cache_year = int(cache_time_date[:4])   # 
        if actual_year - cache_year > 0:
            flag = False
            arr = False
            return flag, arr
        else:
            actual_month = int(actual_time_date[5:7]) # получаем актуальный месяц
            cache_month = int(cache_time_date[5:7])   # получаем месяц из КЭШа
            actual_day = int(actual_time_date[8:10])  # получаем актуальный день     
            cache_day = int(cache_time_date[8:10])    # получаем день из КЭШа
            actual_hour = int(actual_time_date[11:13])# получаем актуальный час
            cache_hour = int(cache_time_date[11:13])  # получаем час из КЭШа
            aim_track_id = city + cache_time_date     # получаем целевой Track_id для получения нужного Json bp КЭША
            print (aim_track_id)
            search_name = aim_track_id # задаем ID для поиска
            sql = "SELECT JSON FROM cache WHERE ID=?" # ищем Json по заданному ID
            cursor.execute(sql, [(search_name)])
            ans = cursor.fetchall() # найденный JSON записываем в переменную
            ans = ans[0][0]
            json = eval(ans) # преобразовываем строку оратно в словарь
            
            if actual_month - cache_month >= 2:  # если разница в месяцах больше 2х то точно не берем Json из КЭШа
                flag = False
                arr = False
                return flag, arr
            elif actual_month - cache_month == 1: # если разница в месяцах равна 1 - смотрим варианты
                months_1 = [4,6,9,11]
                months_2 = [1,3,5,7,8,10,12]
                if actual_day == 30 and cache_day == 1 and cache_month in months_1:
                    temp_hour = 24 - cache_hour
                    if (temp_hour + actual_hour) < 12:
                        flag = True
                        arr = json
                        return flag, arr
                    else:
                        flag = False
                        arr = False
                        return flag, arr
                elif actual_day == 31 and cache_day == 1 and cache_month in months_2:
                    temp_hour = 24 - cache_hour
                    if (temp_hour + actual_hour) < 12:
                        flag = True
                        arr = json
                        return flag, arr
                    else:
                        flag = False
                        arr = False
                        return flag, arr
                else:
                    flag = False
                    arr = False
                    return flag, arr
            elif actual_month - cache_month == 0: # если даты в том же месяце то смотри разницу по дням 
                if (actual_day - cache_day) >= 2 : # если разница в днях 2 и более то данные в КЕШе точно не актуальны
                    flag = False
                    arr = False
                    return flag, arr
                elif actual_day - cache_day == 1:  # если разница в днях составляет 1 - смотрим разницу в часах
                    temp_hour = 24 - cache_hour
                    if (temp_hour + actual_hour) < 12:
                        flag = True
                        arr = json
                        return flag, arr
                    else:
                        flag = False
                        arr = False
                        return flag, arr
                elif actual_day - cache_day == 0:  # если разница в днях составляет 0 - смотрим разницу в часах
                    if actual_hour - cache_hour < 12:
                        flag = True
                        arr = json
                        return flag, arr
                    else:
                        flag = False
                        arr = False
                        return flag, arr

        

def get_forecast(name, flight_number):
    """Функция получает погоду для городов отправки и прибытия в соответствующее время.
        """
    conn = sqlite3.connect("forecast_bot_database.db") # открываем базу
    cursor = conn.cursor()
    conn.commit()

    track_id = name + flight_number

    sql = "SELECT city_of_departure FROM M_Flights WHERE Track_id=?" # ищем город отправления по Track_id
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденный город записываем в переменную
    print(ans)
    city_of_departure = ans[0][0] # получили город отправления
    print(city_of_departure)

    sql = "SELECT time_of_departure FROM M_Flights WHERE Track_id=?" # ищем время отправления по Track_id
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденное время записываем в переменную
    time_of_departure = ans[0][0] # получили время отправления
    ans1 , ans2 = check_in_cache(city_of_departure) # проверяем данные для данного города в КЕШе
    if ans1:  # если в КЕШе есть актуальный прогноз - берем JSON с погодой из КЕШа 
        print('Json взят из кеша')
        json_1 = ans2
        
        aim_date = time_of_departure[:10] # задаем целевую дату
        aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
        aim_time = time_of_departure[11:13] # задаем целевое время
        
        temp_array_1 = json_1['forecasts'] # вытаскиваем массив словарей из JSON
        count_1 = 0
        for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
            if element['date'] == aim_date:
                index_1 = count_1
                break
            else:
                count_1 +=1
    
        aim_weather =  json_1['forecasts'][count_1]['hours'][int(aim_time)]            
        json_1 = aim_weather # получаем погоду для города отправления
    else: # если в КЕШе нет актуальных данных с погодой берем данные из Яндекс.Погоды
        print('Json взят из Яндекса')
        json_1 = get_weather_from_yandex(time_of_departure, city_of_departure) # получаем погоду для города отправления

    
    sql = "SELECT city_of_arrival FROM M_Flights WHERE Track_id=?" # ищем город прибытия по Track_id
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденный город записываем в переменную
    print(ans)
    city_of_arrival = ans[0][0] # получили город прибытия
    print(city_of_arrival)

    sql = "SELECT time_of_arrival FROM M_Flights WHERE Track_id=?" # ищем время прибытия по Track_id
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденное время записываем в переменную
    print(ans)
    time_of_arrival = ans[0][0] # получили время прибытия
    print(time_of_arrival)
    ans1 , ans2 = check_in_cache(city_of_arrival) # проверяем данные для данного города в КЕШе
    if ans1: # если в КЕШе есть актуальный прогноз - берем JSON с погодой из КЕШа
        print('Json взят из кеша')
        json_2 = ans2
        
        aim_date = time_of_departure[:10] # задаем целевую дату
        aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
        aim_time = time_of_departure[11:13] # задаем целевое время
        
        temp_array_1 = json_2['forecasts'] # вытаскиваем массив словарей из JSON
        count_1 = 0
        for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
            if element['date'] == aim_date:
                index_1 = count_1
                break
            else:
                count_1 +=1
    
        aim_weather =  json_2['forecasts'][count_1]['hours'][int(aim_time)]           
        json_2 = aim_weather # получаем погоду для города прибытия
    else:# если в КЕШе нет актуальных данных с погодой берем данные из Яндекс.Погоды
        print('Json взят из Яндекса')
        json_2 = get_weather_from_yandex(time_of_arrival, city_of_arrival) # получаем погоду для города прибытия
    return json_1, json_2  



        
    
    



