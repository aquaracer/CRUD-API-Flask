import sqlite3
 
conn = sqlite3.connect("forecast_bot_database.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

conn.commit()

track_id = 'C_3129'

sql = "SELECT time_of_arrival FROM M_Flights WHERE Track_id=?" # ищем время прибытия по Track_id
cursor.execute(sql, [(track_id)])
ans = cursor.fetchall() # найденное время записываем в переменную
print(ans)
time_of_arrival = ans[0][0] # получили время прибытия
print(time_of_arrival)

#cursor.execute("""CREATE TABLE Cache
#                  (ID text, city text, date_time_of_creation text, JSON text)
#               """)

#conn.commit()

ID  = 'ID'
city = 'city'
date_time_of_creation = 'date_time_of_creation'
JSON = 'JSON'


new_data = [(ID, city, date_time_of_creation, JSON)]

#cursor.executemany("INSERT INTO Cache VALUES(?,?,?,?)", new_data) # добавляем запись в базу
#conn.commit()

print("Here's a listing of all the records in the Cache:")
for row in cursor.execute("SELECT rowid, * FROM Cache ORDER BY ID"):
    print(row)



#print(cursor.fetchall()) # or use fetchone(), выводим результат поиска
#print(len(ans))    # выводим длину массива
#print(ans)
#print(ans[0][1])

a=9999999        # задаем новый баланс
b= 'Kolya'     # задаем  ID пользователя
c = '"' + b + '"'

#print (c)

sql = """
UPDATE balances     
SET balance ={0} 
WHERE user_id={1} """ #  формулируем запрос   
sql= sql.format(str(a), str(c)) # форматируем запрос
#cursor.execute(sql)
#conn.commit()         # запускаем запрос


user_id_base = '114444443'
table_name = 'card_base_' + user_id_base # создаем название таблицы  
new_table = """CREATE TABLE {0}
                  (card_name text, link_card text)
               """
new_table = new_table.format(table_name)
#print(new_table)
        
#cursor.execute(new_table)
#conn.commit()


card_name = 'lion'
link_card = 'images/lion.jpg'
new_card = [(card_name, link_card)]

#cursor.executemany("INSERT INTO card_base_101l01l01 VALUES (?,?)", new_card) # так добавляем запись в базу
#conn.commit()

#sql = "DELETE FROM card_base_114444443 WHERE card_name = 'Pia'"
 
#cursor.execute(sql)
#conn.commit()


b= 'lion'     # задаем  ID пользователя
c = '"' + b + '"'   # создаем кавычки для ID

sql = "DELETE FROM card_base_cache WHERE card_name = 'The Rack' "
#sql = sql.format(c)
 
#cursor.execute(sql)
#conn.commit()





