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
    
    
    

time_of_arrival = '2019-06-31 00:40'
city_of_arrival = 'Toronto'


get_weather_from_yandex(time_of_arrival, city_of_arrival)
    


