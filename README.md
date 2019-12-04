## CRUD api с использованием кеширования для ускорения запросов

### Техническое задание:
Реализовать простой CRUD api с использованием кеширования для ускорения запросов. Использовать фреймворк Flask.

Представьте, что вы метеорологическая служба, которая предоставляет данные о погоде российским авиакомпаниям. 
Данные вы получаете от сторонних источников (Яндекс.Погода).
Вы должны предоставить клиентам API, с помощью которого они будут получать от вас информацию о погоде.
Допустим с вами работают только три компании: RedAir, BlueAir и GreenAir.
Добавление и удаление рейсов:
Компании передают Вам информацию о рейсах, которые они будут совершать в ближайшее время.

#### * Добавление рейса
PUSH (get запрос): .../push/name/number/cityA/timeA/cityB/timeB

-name - название авиакомпании
-number - номер рейса
-cityA - названия города отправления на английском
-timeA - время отправления в формате yyyy_mm_dd_hh_mm 	  
-cityB - названия города прибытия на английском
-timeA - время прибытия в формате yyyy_mm_dd_hh_mm

#### * Отмена рейса:
POP (get запрос): .../pop/name/number 
-name - название авиакомпании
-number - номер рейса

#### * Запрос погоды для рейса:
Компании запрашивает погоду в городах вылета и прилета. Верните
json с информацией о погоде (формат на ваше усмотрение).  

(get запрос): .../weather/<name>/<number>
-name - название авиакомпании
-number - номер рейса 

Информация о погоде должна быть именно во время вылета и прилета по расписанию, а не на текущий момент.
Учтите, что погода обычно не меняется каждую секунду, запросы на сторонние сервисы платные, нужно кешировать.

#### * List (get запрос): .../list/name
name - название авиакомпании
Функция должна вернуть список рейсов авиакомпании которые еще не совершились.

#### * Archive (get запрос): .../archive/name
Функция должна вернуть список всех совершенных рейсов за последний год

#### основные модули

app2.py - Данный  модуль запускает приложение. Каждый запрос обрабатывается соответствующим декоратором и вызывает функцию.
crud_utilities.py - В данном файле записаны все необходимые функции для приложения. Подробное описание содержится в файле.

протестировать приложение можно на сайте http://testflask.ru

#### Краткая инструкция

##### 1. Добавление рейса:
Bвведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/push/name/number/cityA/timeA/cityB/timeB

- name - название авиакомпании
- number - номер рейса
- cityA - названия города отправления на английском
- timeA - время отправления в формате yyyy_mm_dd_hh_mm 	  
- cityB - названия города прибытия на английском
- timeA - время прибытия в формате yyyy_mm_dd_hh_mm

пример запроса:
http://crudapiflask.site/push/B_2/148/Madrid/2019_06_08_19_40/London/2019_06_08_22_15
после отправки запроса браузер вернет сообщение о том что данные добавлены: tasks: " information has been added to the base"

##### 2. Отмена рейса:
Bвведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/pop/name/number 

- name - название авиакомпании
- number - номер рейса

пример запроса:
http://crudapiflask.site/pop/B_2/148
после отправки запроса браузер вернет сообщение о том что данные удалены: tasks: "database entry has been deleted"

##### 3. Запрос погоды для рейса:
Команда возвращает 2 JSON с прогнозом погоды для города отправления и прибытия. Прогноз можно получить не более чем на 7 дней вперед. Если дата предстоящего рейса более чем 7 дней позже текущей даты вы получите сообщение о том что прогноз на данную дату не доступен.
Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/weather/<name>/<number>

-name - название авиакомпании
-number - номер рейса 

пример запроса:
http://crudapiflask.site/weather/B_2/148
после отправки запроса браузер вернет 2 JSON с данными о погоде в городе отправления и прибытия:

{"forecast for city of arrival":{"_source":"19,22","condition":"cloudy","daytime":"d","feels_like":17,"humidity":64,"icon":"bkn_d","polar":false,"prec_mm":0,"prec_period":360,"prec_prob":0,"pressure_mm":759,"pressure_pa":1012,"soil_moisture":0.21,"soil_temp":21,"temp_avg":19,"temp_max":21,"temp_min":17,"wind_dir":"nw","wind_gust":9,"wind_speed":3.4},
"forecast for city of departure":{"_source":"20,23","condition":"clear","daytime":"d","feels_like":33,"humidity":20,"icon":"skc_d","polar":false,"prec_mm":0,"prec_period":360,"prec_prob":0,"pressure_mm":699,"pressure_pa":932,"soil_moisture":0.1,"soil_temp":38,"temp_avg":35,"temp_max":38,"temp_min":31,"uv_index":1,"wind_dir":"sw","wind_gust":10.5,"wind_speed":1.9}}

##### 4. List (get запрос).
Возвращает список рейсов авиакомпании которые еще не совершились.

Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/list/name
name - название авиакомпании

пример запроса:
http://crudapiflask.site/list/etihat
после отправки запроса браузер вернет JSON со списком рейсов авиакомпании, которые еще не совершились либо сообщение о том что таких рейсов нет: 

{"forthcoming flights":[[{"flight number":"201"},{"city of departure":"Madrid"},{"time of departure":"2019-08-08 19:50"},{"city of arrival":"London"},{"time of departure":"2019-08-08 22:15"}]]}

##### 5. Archive (get запрос).
Возвращает список всех совершенных рейсов за последний год

Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/archive/name
name - название авиакомпании

пример запроса:
http://crudapiflask.site/archive/etihat
после отправки запроса браузер вернет JSON список рейсов, cовершенных за последний год либо сообщение о том что таких рейсов нет: 

{"completed flights":[[{"flight number":"201"},{"city of departure":"Madrid"},{"time of departure":"2019-05-11 19:50"},{"city of arrival":"London"},{"time of departure":"2019-05-11 22:15"}]]}
