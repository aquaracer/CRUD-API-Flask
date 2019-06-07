import sqlite3


conn = sqlite3.connect("forecast_bot_database.db") # открываем базы
cursor = conn.cursor()

conn.commit()


#cursor.execute("""CREATE TABLE M_Flights
#                  (Track_id text, flight_number text, city_of_departure text,
#                  time_of_departure text, city_of_arrival, time_of_arrival text)
#               """)
#
#conn.commit()

res = [] # создаем пустой массив для результатов
Track_ID ='C_3198' 
city = 'Osaka'
city = '"' + city + '"'   # создаем кавычки для city
sql = "SELECT date_time_of_creation FROM Cache WHERE city={0}" # ищем записи с заданным именем
sql=sql.format(city)
cursor.execute(sql)
ans = cursor.fetchall() # найденные записи заносим в массив
print(len(ans))    # выводим длину массива. 

if len(ans) < 1:# если в массиве ничего нет - значит города нет в КЕШе и получить JSON из КЕШа не получится
    flag = False
    arr = False
    return flag
else:
    cache_time_date = max(ans) # получили время введения в КЕШ самых актуальных данных
    actual_time_date = str(datetime.datetime.now()) # получаем актуальное время
    actual_time_date = actual_time_date[:19]
    actual_year = int(actual_time_date[:4]) # получаем актуальный год в формате ИНТ
    cache_year = int(cache_time_date[:4])
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
        
        search_name = aim_track_id # задаем ID для поиска
        sql = "SELECT JSON FROM cache WHERE ID=?" # ищем Json по заданному ID
        cursor.execute(sql, [(search_name)])
        ans = cursor.fetchall() # найденный JSON записываем в переменную
        json = ans
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
        elif actual_month - cache_month == 0:
            if actual_day - cache_day >= 2:
                flag = False
                arr = False
                return flag, arr
            elif actual_day - cache_day == 1:
                temp_hour = 24 - cache_hour
                if (temp_hour + actual_hour) < 12:
                    flag = True
                    arr = json
                    return flag, arr
                else:
                    flag = False
                    arr = False
                    return flag, arr
            elif actual_day - cache_day == 0:
                if actual_hour - cache_hour < 12:
                    flag = True
                    arr = json
                    return flag, arr
                else:
                    flag = False
                    arr = False
                    return flag, arr
                

                
                    
print(ans)         # выводим массив




