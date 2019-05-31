import sqlite3

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

    

#test_data = 'C_3/121/Chicago/2019-05-30 19:40/Los Angeles/2019-05-30 21:00'
#push(test_data)




