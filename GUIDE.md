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
http://crudapiflask.site/push/RedAir/110/Madrid/2019_12_14_19_40/London/2019_12_14_22_15
после отправки запроса браузер вернет сообщение о том что данные добавлены: tasks: " information has been added to the base"

##### 2. Отмена рейса:
Bвведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/pop/name/number 

- name - название авиакомпании
- number - номер рейса

пример запроса:
http://crudapiflask.site/pop/RedAir/110
после отправки запроса браузер вернет сообщение о том что данные удалены: tasks: "database entry has been deleted"

##### 3. Запрос погоды для рейса:
Команда возвращает 2 JSON с прогнозом погоды для города отправления и прибытия. Прогноз можно получить не более чем на 7 дней вперед. Если дата предстоящего рейса более чем 7 дней позже текущей даты вы получите сообщение о том что прогноз на данную дату не доступен.
Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter:
http://crudapiflask.site/weather/name/number

- name - название авиакомпании
- number - номер рейса 

пример запроса:
http://crudapiflask.site/weather/RedAir/110
после отправки запроса браузер вернет 2 JSON с данными о погоде в городе отправления и прибытия:
	
###### forecast for city of arrival	
_source	"18,21"
condition	"overcast-and-light-rain"
daytime	"n"
feels_like	-1
humidity	77
icon	"bkn_-ra_n"
polar	false
prec_mm	0.1
prec_period	360
prec_prob	40
pressure_mm	749
pressure_pa	999
soil_moisture	0.39
soil_temp	4
temp_avg	4
temp_max	4
temp_min	4
wind_dir	"sw"
wind_gust	10.2
wind_speed	3.8
###### forecast for city of departure	
_source	"19,22"
condition	"overcast"
daytime	"n"
feels_like	6
humidity	85
icon	"ovc"
polar	false
prec_mm	0
prec_period	360
prec_prob	0
pressure_mm	705
pressure_pa	940
soil_moisture	0.29
soil_temp	10
temp_avg	9
temp_max	9
temp_min	8
wind_dir	"sw"
wind_gust	6.2
wind_speed	2.7



##### 4. List (get запрос).
Возвращает список рейсов авиакомпании которые еще не совершились.

Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter: http://crudapiflask.site/list/name
- name - название авиакомпании

пример запроса:
http://crudapiflask.site/list/etihat
после отправки запроса браузер вернет JSON со списком рейсов авиакомпании, которые еще не совершились либо сообщение о том что таких рейсов нет: 

{"forthcoming flights":[[{"flight number":"201"},{"city of departure":"Madrid"},{"time of departure":"2019-08-08 19:50"},{"city of arrival":"London"},{"time of departure":"2019-08-08 22:15"}]]}

##### 5. Archive (get запрос).
Возвращает список всех совершенных рейсов за последний год

Bведите в адресной строке браузера запрос в приведенном ниже формате и нажмите enter: http://crudapiflask.site/archive/name
- name - название авиакомпании

пример запроса:
http://crudapiflask.site/archive/etihat
после отправки запроса браузер вернет JSON список рейсов, cовершенных за последний год либо сообщение о том что таких рейсов нет: 

{"completed flights":[[{"flight number":"201"},{"city of departure":"Madrid"},{"time of departure":"2019-05-11 19:50"},{"city of arrival":"London"},{"time of departure":"2019-05-11 22:15"}]]}
