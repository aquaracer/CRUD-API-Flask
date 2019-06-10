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
    номер рейса              - берем из входных данных
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
    import datetime
    
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

        actual_time_date = datetime.datetime.now()  # получаем актуальное время
        cache_time_date= cache_time_date[0]
        print(cache_time_date)
        print(type(cache_time_date))
        from datetime import datetime
        cache_time_date = datetime.strptime(cache_time_date, '%Y-%m-%d %H:%M:%S') # переводим дату и время из строки в соответствующий формат           
        delta = actual_time_date - cache_time_date
        days_delta = delta.days
        if days_delta == 0 : #  если разница в днях равна 0
            total_seconds = delta.seconds
            if total_seconds < 43200:  # если разница во времени менее 12 часов - берем погоду из КЕШа
                aim_track_id = city + str(cache_time_date)     # получаем целевой Track_id для получения нужного Json bp КЭША
                #print (aim_track_id)
                search_name = aim_track_id # задаем ID для поиска
                sql = "SELECT JSON FROM cache WHERE ID=?" # ищем Json по заданному ID
                cursor.execute(sql, [(search_name)])
                ans = cursor.fetchall() # найденный JSON записываем в переменную
                ans = ans[0][0]
                json = eval(ans)    
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
        

def get_city_json(track_id, direction):
    """ Функция на входе получает Track_id и напрвление полета(отправление и прибытие).
        По заданным данным находит в базе соответствующий город и время. Далее проверяет КЕШ (функция check_in_cash) на наличие актуальной
        записи по заданному городу. Если находит в КЕШе - возвращает JSON с погодой для заданного города на заданное
        время. Если не находит в КЕШе - берет данные в Яндекс погоде(функция get_weather_from_yandex) и
        возвращает JSON с погодой для заданного города на заданное время"""
    
    conn = sqlite3.connect("forecast_bot_database.db") # открываем базу
    cursor = conn.cursor()
    conn.commit()

    sql = "SELECT city_of_{0} FROM M_Flights WHERE Track_id=?" # ищем город отправления(или прибытия в зависимости от переменной direction) по Track_id
    sql = sql.format(direction)
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденный город записываем в переменную
    print(ans)
    city_of_flight = ans[0][0] # получили город отправления(или прибытия в зависимости от переменной direction)
    print(city_of_flight)

    sql = "SELECT time_of_{0} FROM M_Flights WHERE Track_id=?" # ищем время отправления(или прибытия в зависимости от переменной direction) по Track_id
    sql = sql.format(direction)
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденное время записываем в переменную
    time_of_flight = ans[0][0] # получили время 
    ans1 , ans2 = check_in_cache(city_of_flight) # проверяем данные для данного города в КЕШе
    if ans1:  # если в КЕШе есть актуальный прогноз - берем JSON с погодой из КЕШа 
        print('Json взят из кеша')
        json_final = ans2
        print(json_final['now_dt'])
        
        aim_date = time_of_flight[:10] # задаем целевую дату
        aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
        aim_time = time_of_flight[11:13] # задаем целевое время
        print (aim_date)
        print (aim_time)
        temp_array_1 = json_final['forecasts'] # вытаскиваем массив словарей из JSON
        count_1 = 0
        for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
            if element['date'] == aim_date:
                index_1 = count_1
                break
            else:
                count_1 +=1

        print(json_final['forecasts'][count_1]['hours'])    
        aim_weather =  json_final['forecasts'][count_1]['hours'][int(aim_time)]            
        json_final = aim_weather # получаем погоду для города отправления
        return json_final
    else: # если в КЕШе нет актуальных данных с погодой берем данные из Яндекс.Погоды
        print('Json взят из Яндекса')
        json_1 = get_weather_from_yandex(time_of_flight, city_of_flight) # получаем погоду для города отправления
        return json_1


def get_forecast(name, flight_number):
    """Функция получает погоду для городов отправки и прибытия в соответствующее время по номеру рейса.
        """
    track_id = name + flight_number # формируем Track_id
    json_1 = get_city_json(track_id, "departure")
    json_2 = get_city_json(track_id, "arrival")

    return json_1, json_2  



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


def list(name):
    conn = sqlite3.connect("forecast_bot_database.db") #
    cursor = conn.cursor() # подключаемся к базе

    res = []
    #print("Here's a listing of all the records in the M_Flights:")
    for row in cursor.execute("SELECT rowid, * FROM M_Flights ORDER BY time_of_departure"):
        temp_1= row[1][:3]
        #print (temp_1)
        if temp_1 == name:
            if row[4] != "time_of_departure":
                import datetime
                temp = row[4]
                actual_time_date = datetime.datetime.now()
                from datetime import datetime
                temp = datetime.strptime(temp, '%Y_%m_%d_%H_%M') # переводим дату и время из строки в соответствующий формат

                if actual_time_date < temp:
                    #print(row)
                    res.append(row[1:])

    if len(res) == 0:
        res = 'There are no forthcoming flights'
        flag = False
        return flag, res
    elif len(res) > 0:
        flag = True
        return flag, res


def archive(name):
    conn = sqlite3.connect("forecast_bot_database.db") #
    cursor = conn.cursor() # подключаемся к базе

    res = []
    #print("Here's a listing of all the records in the M_Flights:")
    for row in cursor.execute("SELECT rowid, * FROM M_Flights ORDER BY time_of_departure"):
        temp_1= row[1][:3]
        #print (temp_1)
        if temp_1 == name:
            if row[4] != "time_of_departure":
                import datetime
                temp = row[4]
                actual_time_date = datetime.datetime.now()
                from datetime import datetime
                temp = datetime.strptime(temp, '%Y_%m_%d_%H_%M') # переводим дату и время из строки в соответствующий формат
                delta = actual_time_date - temp
                
                if actual_time_date < temp:
                    #print(row)
                    res.append(row[1:])

    if len(res) == 0:
        res = 'There are no forthcoming flights'
        flag = False
        return flag, res
    elif len(res) > 0:
        flag = True
        return flag, res


#b = List('C_3')
#print (b)
    

#j1, j2 = get_forecast('A_1', '162')
#print (j1, j2)
    
#test_flag, test_json = check_in_cache('Chicago')
#test_json = get_weather_from_yandex('2019_06_08_22_15', 'Madrid')
#print (test_flag)
#print(test_json)
#test_json_1, test_json_2 = get_forecast("B_2", "159")
#print (test_json_1)
#print (test_json_2)
#push('B_2', '159', 'Madrid', '2019_06_09_19_40', 'London', '2019_06_09_23_15')
