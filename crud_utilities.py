import sqlite3
import urllib
import urllib.request
import requests
import datetime
import json

def push(name, number, cityA, timeA, cityB, timeB):
    '''Функция заполняет 7 строк таблицы:

 трек_номер(Id) в формате  перевозчик +номер рейса | номер рейса  | 

  город отправления |дата и время отправления| дата и время прибытия | город прибытия | название авиакомпании

    Track ID -перевозчик + номер рейса + время отправления
    номер рейса              - берем из входных данных
    город отправления        - берем из входных данных
    дата и время отправления - берем из входных данных
    город прибытия           - берем из входных данных
    дата и время прибытия    - берем из входных данных
    название авиакомпании    - берем из входных данных '''

    conn = sqlite3.connect("forecast_bot_database.db")  
    cursor = conn.cursor() 
    Track_ID = name + number   # получили данные для 1го столбца
    flight_number=number # получили данные для 2го столбца
    city_of_departure = cityA # получили данные для 3го столбца
    date_time_of_departure = timeA # получили данные для 4го столбца
    city_of_arrival = cityB # получили данные для 5го столбца
    time_of_arrival = timeB # получили данные для 6го столбца
    new_information = [(Track_ID, flight_number, city_of_departure, date_time_of_departure, city_of_arrival, time_of_arrival, name)]
    new_insert = "INSERT INTO M_Flights VALUES (?,?,?,?,?,?,?)"
    cursor.executemany(new_insert, new_information) # добавляем запись в базу
    conn.commit()
    report = ' information has been added to the base' 
    return report

def pop(name, number):
    ''' Функция удаляет запись из базы полетов. Входные данные: название авиакомпании и номер рейса.
    Производится поиск в базе по ключу (название компании + номер рейса). Если запись найдена то происходит ее
    удаление и возвращается подтверждение об удалении.
    Если запись в базе отствует выводится соответствующее сообщение'''
         
    conn = sqlite3.connect("forecast_bot_database.db")
    cursor = conn.cursor() 
    conn.commit()
    res = [] # создаем пустой массив для результатов
    Track_ID =name+number # создаем Track_Id состоящий из имени компании и номера рейса
    for row in cursor.execute("SELECT rowid, * from M_Flights ORDER BY Track_ID"): # создаем массив записей Track_ID
        res.append(row[1])
    if Track_ID in res:  # если Track_ID есть в базе - удаляем запись из базы
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

 ID (в формате: город + дата создания)| город | дата создания | JSON с погодой на неделю
 
        Цель кеширования : уменьшение количества запросов к основному сервису Яндекс.погоды"""

    conn = sqlite3.connect("forecast_bot_database.db") # подключаемся к базе
    cursor = conn.cursor()
    conn.commit()
    date_time_of_creation = str(datetime.datetime.now()) # получили данные для 3го столбца
    date_time_of_creation = date_time_of_creation[:19]
    id_1 = city + date_time_of_creation # получили данные для 1го столбца
    new_data = [(id_1, city, date_time_of_creation, JSON)]
    cursor.executemany("INSERT INTO Cache VALUES(?,?,?,?)", new_data) # добавляем запись в базу
    conn.commit()
          
def check_in_cache(city):    
    """Функция проверяет наличие JSON с погодой в кеше по заданному городу и в случае обнаружения
       актуальных данных возвращается JSON с погодой. 
       Проверка проводится в 2 этапа:
       1 этап. Производится поиск заданного города в КЕШе. Если город не
       найден функция прекращает действие. Если город найден переходим к следующему этапу - проверяем актуальность данных.
       2 этап. проверяем сколько прошло времени с момента создания записи в кеше до актуального запроса.
       Если с момента создания крайней записи в КЕШе до запроса прошло менее 12 часов - то берем запись из КЕШа.
       В противном случае - функция сообщает что запись не найдена"""
    
    conn = sqlite3.connect("forecast_bot_database.db") # открываем базу
    cursor = conn.cursor()
    conn.commit()
    res = [] # создаем пустой массив для результатов
    temp_city = '"' + city + '"'   # создаем кавычки для city
    sql = "SELECT date_time_of_creation FROM Cache WHERE city={0}" # ищем записи с заданным названием города
    sql=sql.format(temp_city)
    cursor.execute(sql)
    ans = cursor.fetchall() # найденные записи заносим в массив     
    if len(ans) < 1:# если в массиве ничего нет - значит города нет в КЕШе и получить JSON из КЕШа не получится
        flag = False
        arr = False
        return flag, arr
    else:     # в противном случае в КЕШе есть как минимум одна запись для данного города
        cache_time_date = max(ans) # получили время введения в КЕШ самых актуальных данных
        actual_time_date = datetime.datetime.now()  # получаем актуальное время
        cache_time_date= cache_time_date[0]
        cache_time_date = datetime.datetime.strptime(cache_time_date, '%Y-%m-%d %H:%M:%S') # переводим дату и время из строки в соответствующий формат           
        delta = actual_time_date - cache_time_date
        days_delta = delta.days
        if days_delta == 0 : #  если разница в днях равна 0 то проводим проверку на разницу в секундах
            total_seconds = delta.seconds # высчитываем разницу в секундах
            if total_seconds < 43200:  # если разница во времени менее 12 часов - берем погоду из КЕШа
                aim_track_id = city + str(cache_time_date)     # получаем целевой Track_id для получения нужного Json из КЭША
                search_name = aim_track_id # задаем ID для поиска
                sql = "SELECT JSON FROM cache WHERE ID=?" # ищем Json по заданному ID
                cursor.execute(sql, [(search_name)])
                ans = cursor.fetchall() # найденный JSON записываем в переменную
                ans = ans[0][0]
                json = eval(ans)   # переводим из текста в словарь 
                flag = True # значение переменной означает наличие актуальных данных в КЕШе по городу (True если в КЕШе есть актуальные данные)
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
    city_of_flight = ans[0][0] # получили город отправления(или прибытия в зависимости от переменной direction
    sql = "SELECT time_of_{0} FROM M_Flights WHERE Track_id=?" # ищем время отправления(или прибытия в зависимости от переменной direction) по Track_id
    sql = sql.format(direction)
    cursor.execute(sql, [(track_id)])
    ans = cursor.fetchall() # найденное время записываем в переменную
    time_of_flight = ans[0][0] # получили время
    actual_time_date = datetime.datetime.now()
    temp_time_date = datetime.datetime.strptime(time_of_flight, '%Y_%m_%d_%H_%M')
    delta = temp_time_date - actual_time_date
    if delta.days > 7: # если заданная дата более чем на 7 дней позже текущего момента - прогноз не доступен
        report = 'Forecast is not available for requested date'
        return report
    hour_of_flight = int(time_of_flight[11:13]) # находим час прилета/вылета чтобы определить часть суток, в которой он состоится
    if hour_of_flight >= 0 and hour_of_flight <= 7:
        part_of_day = "night"
    if hour_of_flight >= 5 and hour_of_flight < 12:
        part_of_day = "morning"
    if hour_of_flight >= 12 and hour_of_flight < 17:
        part_of_day = "day"
    if hour_of_flight >17:
        part_of_day = "evening"
    ans1 , ans2 = check_in_cache(city_of_flight) # проверяем данные для данного города в КЕШе
    if ans1:  # если в КЕШе есть актуальный прогноз - берем JSON с погодой из КЕШа 
        json_final = ans2
        aim_date = time_of_flight[:10] # задаем целевую дату
        aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
        print(json_final)
        temp_array_1 = json_final['forecasts'] # вытаскиваем массив словарей из JSON
        count_1 = 0
        for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
            if element['date'] == aim_date:
                index_1 = count_1
                break
            else:
                count_1 +=1
        print(temp_array_1)
        print(count_1)
        aim_weather = json_final['forecasts'][count_1]['parts'][part_of_day] # получаем прогноз для заданной части суток          
        json_final = aim_weather # получаем погоду для города отправления
        return json_final
    else: # если в КЕШе нет актуальных данных с погодой берем данные из Яндекс.Погоды
        json_final = get_weather_from_yandex(time_of_flight, city_of_flight) # получаем погоду для города из Яндекс.Погоды
        return json_final

def get_forecast(name, flight_number):
    """Функция получает погоду для городов отправки и прибытия в соответствующее время по номеру рейса."""
    track_id = name + flight_number # формируем Track_id
    json_1 = get_city_json(track_id, "departure") # получаем словарь с погодой для города отправления
    json_2 = get_city_json(track_id, "arrival") # получаем словарь с погодой для города прибытия
    return json_1, json_2  

def get_weather_from_yandex(date_time, city_name):
    """Входные данные в функцию: дата_время и название города.
       Функция получает JSON с погодой из сервиса Яндекс.погода через API по заданным данным.
       Также производит кеширование(путем вызова функции add_data_to_cache) JSON с погодой на 7 дней
       для заданного города"""

    actual_time_date = datetime.datetime.now()
    temp_time_date = datetime.datetime.strptime(date_time, '%Y_%m_%d_%H_%M')
    delta = temp_time_date - actual_time_date
    if delta.days > 7:
        report = 'Forecast is not available for this date'
        return report
    time_of_flight = int(date_time[11:13])
    if time_of_flight >= 0 and time_of_flight <= 7:
        part_of_day = "night"
    if time_of_flight >= 5 and time_of_flight < 12:
        part_of_day = "morning"
    if time_of_flight >= 12 and time_of_flight < 17:
        part_of_day = "day"
    if time_of_flight >17:
        part_of_day = "evening"
    cur_url = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey=a3d86791-9f7c-483b-bd99-6fa3393d63d5&geocode={0}' # создаем ссылку на запрос координат города
    cur_url = cur_url.format(city_name)  # подставляем нужный город
    r = requests.get(url=cur_url) # через API запрос получаем словарь в формате JSON
    data = r.json()
    data = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'] # находим строку с долготой и широтой
    data = data.split(' ')
    lat = data[1] # записываем широту
    lon = data[0] # записываем долготу   
    cur_url ='https://api.weather.yandex.ru/v1/forecast?lat={0}&lon={1}&hours=true' # создаем ссылку на запрос погоды
    cur_url = cur_url.format(lat,lon) # подставляем долготу и широту заданного города
    header = {'X-Yandex-API-Key': 'f37e1bd3-7bc0-41b3-8e68-d450a5ec79d0'}
    r = requests.get(url=cur_url, headers=header ) # через API запрос получаем словарь в формате JSON
    data = r.json()
    print(data)
    add_data_to_cache(city_name, str(data)) # добавляем в КЕШ город и JSON с погодой
    aim_date = date_time[:10]              # создаем целевую дату(дату рейса) для поиска в JSON
    aim_date = aim_date.replace('_', '-')  # приводим дату к формату годному для Яндекса
    aim_time = date_time[11:13]            # создаем целевое время(время рейса) для поиска в JSON 
    temp_array_1 = data['forecasts']   # вытаскиваем массив словарей из JSON
    count_1 = 0
    for element in temp_array_1:    # в массиве находим индекс словаря, в котором хранятся данные о погоде на заданную ДАТУ
        if element['date'] == aim_date:
            index_1 = count_1
            break
        else:
            count_1 +=1
    print(temp_array_1)
    print(count_1)
    print(data['forecasts'][count_1])
    aim_weather =  data['forecasts'][count_1]['parts'][part_of_day]  # вытаскиваем прогноз погоды в заданные дату и время         
    return aim_weather

def list_1(company_name):
    """ Входные данные: название авиакомпании. Функция возвращает список рейсов(в формате JSON)
        авиакомпании, которые еще не совершились.
        Если таких рейсов нет - функция возвращает JSON  с соответствующим сообщением"""
    
    conn = sqlite3.connect("forecast_bot_database.db") 
    cursor = conn.cursor() # подключаемся к базе
    company_name = '"' + company_name + '"'   # создаем кавычки для company_name
    sql = "SELECT * FROM M_Flights WHERE name={0}" # ищем записи с заданным названием авиакомпании
    sql=sql.format(company_name)
    cursor.execute(sql)
    ans = cursor.fetchall() # найденные записи заносим в массив   
    print (ans)
    res = []
    for element in ans:
        actual_time_date = datetime.datetime.now() # находим текущую дату и время
        temp = element[3]
        temp = datetime.datetime.strptime(temp, '%Y_%m_%d_%H_%M') # переводим дату и время из строки в соответствующий формат
        if actual_time_date < temp: # сравниваем текущее время и время вылета. если текущее значение времени меньше значит рейс еще не состоялся
            print(element)
            res.append(element) # добавляем в массив предстоящий рейс
    if len(res) == 0: # если  в массиве результатов нет элементов значит предстоящих рейсов нет
        res = 'There are no forthcoming flights' # возвращаем соответствующее сообщение
        flag = False
        return flag, res
    elif len(res) > 0: # если в массиве есть хоть один элемент - возвращаем массив
        for i in range(len(res)):
            res[i] = list(res[i])
            res[i] = res[i][1:-1]
            res[i][0] = {'flight number': res[i][0]}
            res[i][1] = {'city of departure': res[i][1]}
            res[i][2] = str(datetime.datetime.strptime(res[i][2], '%Y_%m_%d_%H_%M'))
            res[i][2] = res[i][2][:-3]
            res[i][2] = {'time of departure': res[i][2]}
            res[i][3] = {'city of arrival': res[i][3]}
            res[i][4] = str(datetime.datetime.strptime(res[i][4], '%Y_%m_%d_%H_%M'))
            res[i][4] = res[i][4][:-3]
            res[i][4] = {'time of departure': res[i][4]}
        flag = True
        return flag, res

def archive(company_name):
    """ Входные данные: название авиакомпании. Функция возвращает список рейсов(в формате JSON)
        совершенных за последний год.
        Если таких рейсов нет - функция возвращает JSON  с соответствующим сообщением"""
    
    conn = sqlite3.connect("forecast_bot_database.db") 
    cursor = conn.cursor() # подключаемся к базе
    company_name = '"' + company_name + '"'   # создаем кавычки для company_name
    sql = "SELECT * FROM M_Flights WHERE name={0}" # ищем рейсы заданной авиакомпании
    sql=sql.format(company_name)
    cursor.execute(sql)
    ans = cursor.fetchall() # найденные записи заносим в массив   
    print (ans)
    res = []
    for element in ans:
        actual_time_date = datetime.datetime.now() # находим текущую дату и время
        temp = element[5] # находим время прилета
        temp = datetime.datetime.strptime(temp, '%Y_%m_%d_%H_%M') # переводим дату и время из строки в соответствующий формат
        if actual_time_date > temp: # сравниваем текущее время и время прилета. если текущее значение времени больше значит рейс состоялся
            print(element)
            res.append(element) # добавляем в массив состоявшийся рейс
    if len(res) == 0: # если в массиве результатов нет элементов значит состоявшихся рейсов нет
        res = 'There are no flights in archive' # возвращаем соответствующее сообщение
        flag = False
        return flag, res
    elif len(res) > 0: # если в массиве есть хоть один элемент - возвращаем массив
        for i in range(len(res)):
            res[i] = list(res[i])
            res[i] = res[i][1:-1]
            res[i][0] = {'flight number': res[i][0]}
            res[i][1] = {'city of departure': res[i][1]}
            res[i][2] = str(datetime.datetime.strptime(res[i][2], '%Y_%m_%d_%H_%M'))
            res[i][2] = res[i][2][:-3]
            res[i][2] = {'time of departure': res[i][2]}
            res[i][3] = {'city of arrival': res[i][3]}
            res[i][4] = str(datetime.datetime.strptime(res[i][4], '%Y_%m_%d_%H_%M'))
            res[i][4] = res[i][4][:-3]
            res[i][4] = {'time of departure': res[i][4]}
        flag = True
        return flag, res

#res_1 = list_1('etihat')
#print(res_1)

#res = get_weather_from_yandex('2019_07_14_19_50', 'London')
#print(res)

#res = get_city_json('etihat221', "departure")
#print(res)
