# -*- coding: utf-8 -*-
import config
import telebot
import pickle
from datetime import datetime, date, time
import crud_utilities


path, push_data, pop_data, forecast_data = {}, {}, {}, {}
curr_message, name_of_receiver, track_number,  pict, file_report, temp_balance_text, balance_report, user_cards_base, report, img = {}, {}, {}, {}, {}, {}, {}, {}, {}, {}


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['help'])
def Help(message):
    text='''Вас приветствует Forecast_Bot!
 Чтобы начать нажмите /Start .
'''
    bot.send_message(message.chat.id, text)
    return

@bot.message_handler(commands=['/Start'])
@bot.message_handler(content_types=["text"])
def crm_main(message):
    global path
    global curr_user_id
    global service_user_id
    global service_user_balance
    
    user_id = str(message.from_user.id)
    curr_message[user_id] = message.text  
    print (user_id)
  
    if user_id not in path.keys():
        path[user_id] = None    

    if path[user_id] == '/PUSH_u':
        push_data[user_id] = curr_message[user_id]
        report[user_id] = crud_utilities.push(push_data[user_id])
        bot.send_message(message.chat.id, report[user_id])
        path[user_id]='command'


    elif path[user_id] == '/POP_u':
        pop_data[user_id] = curr_message[user_id]
        bot.send_message(message.chat.id, 'рейс отменен. Чтобы продолжить нажмите /Start')
        path[user_id]='command'

    elif path[user_id] == '/Get_forecast_u':
        forecast_data[user_id] = curr_message[user_id]
        bot.send_message(message.chat.id, '''Вывожу прогноз погоды
                                             Чтобы продолжить нажмите /Start   ''')
        path[user_id]='command'

    

    elif path[user_id] == 'command':
        if curr_message[user_id] == '/PUSH' :
            bot.send_message(message.chat.id, '''добавьте информацию о рейсе в формате :
                            /<name_air>/<flight_number>/<city_A>/dd_mm_yyyy_hh_mm/<city_B>/dd_mm_yyyy_hh_mm''')
            path[user_id]='/PUSH_u'


        elif curr_message[user_id] == '/POP' :
            bot.send_message(message.chat.id, 'добавьте информацию о рейсе для отмены в формате : /<name_air>/<flight_number><time_A>/')
            path[user_id]='/POP_u' 
    
        elif curr_message[user_id] == '/Get_forecast' :
            bot.send_message(message.chat.id, '''укажите информацию о рейсе для которого хотите
                             : /<name_air>/<flight_number>/<time_A>''')
            path[user_id]='/Get_forecast_u'
            
            
            
           
        elif curr_message[user_id] == '/Start' :
            bot.send_message(message.chat.id, '''
                         вы находитесь в главном меню. вам доступны следующие команды:
                                            /PUSH  - добавление рейса
                                            /POP - отмена рейса
                                            /Get_forecast - запрос прогноза погоды для рейса
                                                 ''')
   



    elif path[user_id] == None:
        if curr_message[user_id] == '/Start' :
            bot.send_message(message.chat.id, '''
                         вы находитесь в главном меню. вам доступны следующие команды:
                                            /PUSH  - добавление рейса
                                            /POP - отмена рейса
                                            /Get_forecast - запрос погоды для рейса''')
                                            

            path[user_id]='command'
            
        else:
            bot.send_message(message.chat.id, 'повторите комманду')

    else:
            bot.send_message(message.chat.id, 'повторите комманду')
    



if __name__ == '__main__':
     bot.polling(none_stop=True)
