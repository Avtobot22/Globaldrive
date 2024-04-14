import telebot
from telebot import types
import datetime
import json
import os
import csv
import threading


# Обработчик команды для выбора пользователей


def load_users():
    file_path = "config.uni"
    if os.path.exists(file_path):
        with open(file_path, "r",encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(file_path, "w",encoding="utf-8") as f:
            json.dump({}, f)
        return {}

def load_pols():
    file_path = "users.uni"
    if os.path.exists(file_path):
        with open(file_path, "r",encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(file_path, "w",encoding="utf-8") as f:
            json.dump({
                "admin_id":"None",
                "allowed_users":[],
                "spis_del_po_date":{},
                "spis_del_po_bort": {},
                "urgent_request": {}
            }, f)
        return {"admin_id":"None",
                "allowed_users":[],
                "spis_del_po_date":{},
                "spis_del_po_bort": {},
                "urgent_request": {}
            }


fl = load_pols()
user_app = {}
user_state = {}
users = load_users()
TOKEN = "6383727891:AAH74Fd_Fc0z57rZleIvAhgooEoXBf5Vc3Y"
bot = telebot.TeleBot(TOKEN)
botman = telebot.TeleBot("6873590008:AAFRWz6IaVOfpHjC_5Qq680IoXvRoluzSJY")
data = ['Дата',"Водитель","Пробег","Ощутимые дефекты","Уровень масла ДВС","Уровень охл.жидкости","Уровень масла ГУР","Состояние тормозной.жид","Состояние AdBlue жидкости","Наружное освещение","Состояние омывателя и щеток С/О","Наличие неисправностей панели приборов","Повреждение шин"]
csv_filename = 'data.csv'
waiting_for_users = False
user_state[fl["admin_id"]]= ""
cel = []
call_data = ''
call_message = ''
drive_kl = False
delit = []
klych =False
def find_row_with_date(csv_file, target_date):
    with open(csv_file, newline='', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        for row in reader:
            if row and row[0] == target_date:
                return row
    return None


def append_or_update_row(csv_file, target_date, data):
    row = find_row_with_date(csv_file, target_date)
    if row:
        # Update existing row
        with open(csv_file, 'r+', newline='', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            rows = list(reader)
            index = rows.index(row)
            rows[index] = data
            file.seek(0)
            writer = csv.writer(file)
            writer.writerows(rows)
            file.truncate()
    else:
        # Append new row
        with open(csv_file, 'a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(data)
def show_dopoln(message):
    global csv_filename
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Актуальные заявки по дате")
    item3 = types.KeyboardButton("Актуальные заявки по бортам")
    markup.add(item2, item3)
    if user_app[message.chat.id]["com"] != ["Нет дефектов"] and user_app[message.chat.id]["date"] not in fl["spis_del_po_date"].keys():
        pol1 = "1)Уровень масла ДВС:" + user_app[message.chat.id]["app"]["engine_oil"] + "\n"
        pol2 = "2)Уровень охл.жидкости:" + user_app[message.chat.id]["app"]["cooling_liquid"] + "\n"
        pol3 = "3)Уровень масла ГУР:" + user_app[message.chat.id]["app"]["GUR_oil"] + "\n"
        pol4 = "4)Состояние тормозной.жид:" + ", ".join(
            map(str, user_app[message.chat.id]["app"]["bracking_system"])) + "\n"
        pol5 = "5)Состояние AdBlue жидкости:" + user_app[message.chat.id]["app"]["adblue_system"] + "\n"
        pol6 = "6)Наружное освещение:" + ", ".join(
            map(str, user_app[message.chat.id]["app"]["lighting_system"])) + "\n"
        pol7 = "7)Состояние омывателя и щеток С/О:" + ", ".join(
            map(str, user_app[message.chat.id]["app"]["washer_system"])) + "\n"
        pol8 = "8)Наличие неисправностей панели приборов:" + ", ".join(
            map(str, user_app[message.chat.id]["app"]["dashboard_system"])) + "\n"
        pol9 = "9)Повреждение шин:" + ", ".join(
            map(str, user_app[message.chat.id]["app"]["tires_system"])) + "\n"
        pol10 = "10)Наличие ощутимых дефектов:" + ", ".join(map(str, user_app[message.chat.id]["com"]))
        pol11 = "Водитель:" + users[str(message.chat.id)]["driver"] + "\n"
        pol12 = "Дата:" + user_app[message.chat.id]["date"] + "\n"
        p = [pol12, pol11, pol1, pol2, pol3, pol4, pol5, pol6, pol7, pol8, pol9, pol10]
        st = ''
        for pl in p:
            if pl.split(":")[1] not in ["Нет неисправностей\n", "Нет дефектов\n", "Нет повреждений\n", "\n", "MAX\n"]:
                st += pl
        st = "Срочная заявка\n"+st
        botman.send_message(fl["admin_id"], st, reply_markup=markup)
    else:
        botman.send_message(fl["admin_id"],"Новая заявка/Одна из заявок обновлена", reply_markup=markup)
    text1 = {
        "driver": users[str(message.chat.id)]["driver"],
        "probeg": users[str(message.chat.id)]["probeg"],
        "app": user_app[message.chat.id]["app"],
        "com": user_app[message.chat.id]["com"]
    }
    text2 = {
        "date": user_app[message.chat.id]["date"],
        "probeg": users[str(message.chat.id)]["probeg"],
        "app": user_app[message.chat.id]["app"],
        "com": user_app[message.chat.id]["com"]
    }
    klych = users[str(message.chat.id)]["driver"] + ":" + user_app[message.chat.id]["date"]
    fl["spis_del_po_date"][user_app[message.chat.id]["date"]] = text1
    fl["spis_del_po_bort"][klych] = text2
    save_pols()
    dat = [user_app[message.chat.id]["date"],users[str(message.chat.id)]["driver"],users[str(message.chat.id)]["probeg"],user_app[message.chat.id]["com"]]
    for val in user_app[message.chat.id]["app"].values():
        dat.append(val)
    append_or_update_row(csv_filename,user_app[message.chat.id]["date"],dat)
    # ///////////////////////////////////////
    pol1 = "1)Уровень масла ДВС:" + user_app[message.chat.id]["app"]["engine_oil"] + "\n"
    pol2 = "2)Уровень охл.жидкости:" + user_app[message.chat.id]["app"]["cooling_liquid"] + "\n"
    pol3 = "3)Уровень масла ГУР:" + user_app[message.chat.id]["app"]["GUR_oil"] + "\n"
    pol4 = "4)Состояние тормозной.жид:" + ", ".join(
        map(str, user_app[message.chat.id]["app"]["bracking_system"])) + "\n"
    pol5 = "5)Состояние AdBlue жидкости:" + ", ".join(
        map(str, user_app[message.chat.id]["app"]["adblue_system"])) + "\n"
    pol6 = "6)Наружное освещение:" + ", ".join(map(str, user_app[message.chat.id]["app"]["lighting_system"])) + "\n"
    pol7 = "7)Состояние омывателя и щеток С/О:" + ", ".join(
        map(str, user_app[message.chat.id]["app"]["washer_system"])) + "\n"
    pol8 = "8)Наличие неисправностей панели приборов:" + ", ".join(
        map(str, user_app[message.chat.id]["app"]["dashboard_system"])) + "\n"
    pol9 = "9)Повреждение шин:" + ", ".join(map(str, user_app[message.chat.id]["app"]["tires_system"])) + "\n"
    pol10 = "10)Наличие ощутимых дефектов:" + ", ".join(map(str, user_app[message.chat.id]["com"]))
    bot.send_message(message.chat.id, pol1 + pol2 + pol3 + pol4 + pol5 + pol6 + pol7 + pol8 + pol9 + pol10,reply_markup=types.ReplyKeyboardRemove())
    user_state[message.chat.id] = "dopoln"
def write_csv_header(filename):
    # Заголовки для CSV файла
    csv_headers = data
    # Запись заголовков в CSV файл
    with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:  # Используем utf-8-sig для совместимости с Excel
        writer = csv.writer(file)
        writer.writerow(csv_headers)

if not os.path.exists(csv_filename):
    write_csv_header(csv_filename)

def write_csv_data(filename,data1,data2):
    # Список значений для CSV файла
    csv_mass = []
    csv_mass.append(data1["date"])
    csv_mass.append(data2["driver"])
    csv_mass.append(data2["probeg"])
    csv_mass.append(data1["com"])
    for val in data1["app"].values():
        csv_mass.append(val)

    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(csv_mass)

def write_csv_data_vup(filename,data1,dt):
    # Список значений для CSV файла
    csv_mass = []
    csv_mass.append(dt)
    csv_mass.append(data1["driver"])
    csv_mass.append(data1["probeg"])
    csv_mass.append(data1["com"])
    for val in data1["app"].values():
        csv_mass.append(val)
    csv_mass.append("-выполнено")
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow(csv_mass)

def show_admin(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Актуальные заявки по дате")
    item3 = types.KeyboardButton("Актуальные заявки по бортам")
    markup.add(item2, item3)
    botman.send_message(chat_id, "Список заявок обновлен", reply_markup=markup)

# def check_time():
#     while True:
#         # for kl in list(user_app.keys()):
#         #     if str(kl) in users.keys():
#         #         dl = user_app[kl]
#         #         pl = users[str(kl)]
#         #         if dl["com"] !=["Нет дефектов"] and dl["date"]!="":
#         #             write_csv_data(csv_filename, dl, pl)
#         #             bot.send_message(kl,"Заявка отправлена в срочном порядке")
#         #             botman.send_message(fl["admin_id"],"Срочная заявка")
#         #             pol1 = "1)Уровень масла ДВС:" + user_app[kl]["app"]["engine_oil"] + "\n"
#         #             pol2 = "2)Уровень охл.жидкости:" + user_app[kl]["app"]["cooling_liquid"] + "\n"
#         #             pol3 = "3)Уровень масла ГУР:" + user_app[kl]["app"]["GUR_oil"] + "\n"
#         #             pol4 = "4)Состояние тормозной.жид:" + ", ".join(
#         #                 map(str, user_app[kl]["app"]["bracking_system"])) + "\n"
#         #             pol5 = "5)Состояние AdBlue жидкости:" + user_app[kl]["app"]["adblue_system"] + "\n"
#         #             pol6 = "6)Наружное освещение:" + ", ".join(
#         #                 map(str, user_app[kl]["app"]["lighting_system"])) + "\n"
#         #             pol7 = "7)Состояние омывателя и щеток С/О:" + ", ".join(
#         #                 map(str, user_app[kl]["app"]["washer_system"])) + "\n"
#         #             pol8 = "8)Наличие неисправностей панели приборов:" + ", ".join(
#         #                 map(str, user_app[kl]["app"]["dashboard_system"])) + "\n"
#         #             pol9 = "9)Повреждение шин:" + ", ".join(
#         #                 map(str, user_app[kl]["app"]["tires_system"])) + "\n"
#         #             pol10 = "10)Наличие ощутимых дефектов:" + ", ".join(map(str, user_app[kl]["com"]))
#         #             pol11 = "Водитель:"+users[str(kl)]["driver"]+"\n"
#         #             pol12 = "Дата:"+user_app[kl]["date"]+"\n"
#         #             p = [pol12,pol11, pol1, pol2, pol3, pol4, pol5, pol6, pol7, pol8, pol9, pol10]
#         #             st = ''
#         #             for pl in p:
#         #                 if pl.split(":")[1] not in ["Нет неисправностей\n", "Нет дефектов\n", "Нет повреждений\n","\n","MAX\n"]:
#         #                     st += pl
#         #             markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#         #             item2 = types.KeyboardButton("Актуальные заявки по дате")
#         #             item3 = types.KeyboardButton("Актуальные заявки по бортам")
#         #             markup.add(item2, item3)
#         #             show_keyboard(kl)
#         #             user_state[kl]=""
#         #             botman.send_message(fl["admin_id"],st,reply_markup=markup)
#         #             text1 = {
#         #                 "driver":users[str(kl)]["driver"],
#         #                 "probeg":users[str(kl)]["probeg"],
#         #                 "app":user_app[kl]["app"],
#         #                 "com":user_app[kl]["com"]
#         #             }
#         #             text2 = {
#         #                 "date": user_app[kl]["date"],
#         #                 "probeg": users[str(kl)]["probeg"],
#         #                 "app": user_app[kl]["app"],
#         #                 "com": user_app[kl]["com"]
#         #             }
#         #             klych = users[str(kl)]["driver"]+":"+user_app[kl]["date"]
#         #             fl["spis_del_po_date"][user_app[kl]["date"]]=text1
#         #             fl["spis_del_po_bort"][klych]=text2
#         #             save_pols()
#         #             del user_app[kl]
#         # print(str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":"+ str(datetime.datetime.now().second))
#         if str(datetime.datetime.now().hour) + ":" + str(datetime.datetime.now().minute) + ":"+ str(datetime.datetime.now().second)== "22:30:00":
#             for key in list(user_app.keys()):
#                 if str(key) in users.keys():
#                     # dt = user_app[key]
#                     # pt = users[str(key)]
#                     # write_csv_data(csv_filename,dt,pt)
#                     show_keyboard(key)
#                     user_state[key] = ""
#                     del user_app[key]
#                 show_admin(fl["admin_id"])
#         time.sleep(1)





def save_users():
    with open("config.uni", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False)

def save_pols():
    with open("users.uni", "w", encoding="utf-8") as f:
        json.dump(fl, f, ensure_ascii=False)

def show_keyboard(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Заполнить карту ежедневного осмотра")
    markup.add(item2)
    bot.send_message(chat_id, "Для заполнения карты нажмите на кнопку", reply_markup=markup)


def show_update_keyboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Да")
    item3 = types.KeyboardButton("Нет")
    markup.add(item2,item3)
    pol1 = "Гос.номер:"+users[str(message.chat.id)]["gos_nomer"]
    pol2 = "Водитель:" + users[str(message.chat.id)]["driver"]
    bot.send_message(message.chat.id, "Проверьте правильность данных:"+"\n"+pol1+"\n"+pol2, reply_markup=markup)
    user_state[message.chat.id]="correction"



def show_engine(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("MAX")
    item3 = types.KeyboardButton("Ниже нормы")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Уровень масла", reply_markup=markup)
    user_state[message.chat.id] = "engine_oil"

def show_cool(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("MAX")
    item3 = types.KeyboardButton("Ниже нормы")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Уровень охл.жидкости", reply_markup=markup)
    user_state[message.chat.id] = "cooling_liquid"


def show_GUR(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("MAX")
    item3 = types.KeyboardButton("Ниже нормы")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Уровень масла ГУР", reply_markup=markup)
    user_state[message.chat.id] = "GUR_oil"
def show_bracking(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет дефектов")
    item3 = types.KeyboardButton("Дефект")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Введите состояние тормозной жид.",reply_markup=markup)
    user_state[message.chat.id] = "bracking_system"
def show_adblue(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("MAX")
    item3 = types.KeyboardButton("Ниже нормы")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Уровень AdBlue жид.", reply_markup=markup)
    user_state[message.chat.id] = "adblue_system"

def show_lighting(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет неисправностей")
    item3 = types.KeyboardButton("Неисправность")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Наличие неисправностей освещения", reply_markup=markup)
    user_state[message.chat.id] = "lighting_system"

def show_washer(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет неисправностей")
    item3 = types.KeyboardButton("Неисправность")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Наличие неисправностей омывателя/щеток С/О", reply_markup=markup)
    user_state[message.chat.id] = "washer_system"

def show_dashboard(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет неисправностей")
    item3 = types.KeyboardButton("Неисправность")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Наличие неисправностей приборной панели", reply_markup=markup)
    user_state[message.chat.id] = "dashboard_system"

def show_tires(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет повреждений")
    item3 = types.KeyboardButton("Повреждение")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Осмотр шин", reply_markup=markup)
    user_state[message.chat.id] = "tires_system"

def show_problem(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Нет дефектов")
    item3 = types.KeyboardButton("Дефект")
    markup.add(item2, item3)
    bot.send_message(message.chat.id, "Наличие ощутимых дефектов", reply_markup=markup)
    user_state[message.chat.id] = "problem_system"
def show_probeg(message):
    bot.send_message(message.chat.id, "Введите пробег",reply_markup=types.ReplyKeyboardRemove())
    user_state[message.chat.id] = "probeg_system"

def process_user_input(message,sel):
    if sel ==1:
        show_engine(message)
    elif sel ==2:
        show_cool(message)
    elif sel ==3:
        show_GUR(message)
    elif sel ==4:
        show_bracking(message)
    elif sel ==5:
        show_adblue(message)
    elif sel ==6:
        show_lighting(message)
    elif sel ==7:
        show_washer(message)
    elif sel ==8:
        show_dashboard(message)
    elif sel ==9:
        show_tires(message)

def proverka(message):
    c = False
    if message.chat.id in user_state.keys():
        if user_state[message.chat.id] == 'car' or user_state[message.chat.id] == 'zav_gar':
            c = True
    return c
def show_rol_avt(message):
    bot.send_message(message.chat.id, "Ввведите пароль для роли  Автомобиль")
    user_state[message.chat.id] = "car"

def show_rol_man(message):
    botman.send_message(message.chat.id, "Ввведите пароль для роли  Зав.гар")
    user_state[message.chat.id] = "zav_gar"
def botPoll():
    global poll
    if poll ==0:
        botman.polling(none_stop=True)
        poll = 1
poll = 0
thread1 = threading.Thread(target=botPoll)
# time_thread = threading.Thread(target=check_time)
# while True:
#     try:
@botman.message_handler(commands=['start'])
def starts(message):
    if message.chat.id == fl["admin_id"]:
        show_admin(message.chat.id)
    else:
        show_rol_man(message)


@botman.message_handler(commands=['zadachi_po_date'], func=lambda message: (message.chat.id == fl["admin_id"]))
def zadachi_po_date(message):
    if fl["spis_del_po_date"] == {}:
        botman.send_message(message.chat.id, "Актуальных заявок нет")
    else:
        c = 1
        mas_message = []
        sorted_data = dict(sorted(fl["spis_del_po_date"].items(), key=lambda x: x[0]))
        shablon_slov = {
            "engine_oil": "{})Уровень масла ДВС:{}\n",
            "cooling_liquid": "{})Уровень охл.жидкости:{}\n",
            "GUR_oil": "{})Уровень масла ГУР:{}\n",
            "bracking_system": "{})Состояние тормозной.жид:{}\n",
            "adblue_system": "{})Состояние AdBlue жидкости:{}\n",
            "lighting_system": "{})Наружное освещение:{}\n",
            "washer_system": "{})Состояние омывателя и щеток С/О:{}\n",
            "dashboard_system": "{})Наличие неисправностей панели приборов:{}\n",
            "tires_system": "{})Повреждение шин:{}\n",
            "com": "{})Наличие ощутимых дефектов:{}\n"
        }
        lr = ''
        sl = ''
        for key in sorted_data.keys():
            parts = key.split(':')
            t = ':'.join(parts[:3])
            k = ''
            fault = list(filter(lambda x: fl['spis_del_po_date'][key]["app"][x] not in (
                "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []),
                                fl['spis_del_po_date'][key]["app"]))
            for el in fault:
                if el in ("engine_oil", "cooling_liquid", "GUR_oil", "adblue_system"):
                    if list(fl["spis_del_po_date"].keys()).index(key) != len(list(fl["spis_del_po_date"].keys()))-1:
                        index = list(fl["spis_del_po_date"].keys()).index(key)
                        zap = False
                        for kl in list(fl["spis_del_po_date"].keys())[index+1:]:
                            if fl["spis_del_po_date"][key]["driver"] ==fl["spis_del_po_date"][kl]["driver"]:
                                faul = list(filter(lambda x: fl['spis_del_po_date'][kl]["app"][x] not in (
                                    "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []),
                                                    fl['spis_del_po_date'][kl]["app"]))
                                if el in faul:
                                    zap = True
                        if zap ==False:
                            k += shablon_slov[el].format(c, fl['spis_del_po_date'][key]["app"][el])
                    else:
                        k += shablon_slov[el].format(c, fl['spis_del_po_date'][key]["app"][el])
                else:
                    if list(fl["spis_del_po_date"].keys()).index(key) != len(list(fl["spis_del_po_date"].keys()))-1:
                        index = list(fl["spis_del_po_date"].keys()).index(key)
                        zap = False
                        for kl in list(fl["spis_del_po_date"].keys())[index+1:]:
                            if fl["spis_del_po_date"][key]["driver"] ==fl["spis_del_po_date"][kl]["driver"]:
                                faul = list(filter(lambda x: fl['spis_del_po_date'][kl]["app"][x] not in (
                                    "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []),
                                                    fl['spis_del_po_date'][kl]["app"]))
                                if el in faul:
                                    zap = True
                        if zap ==False:
                            k += shablon_slov[el].format(c, ", ".join(map(str, fl['spis_del_po_date'][key]["app"][el])))
                    else:
                        k += shablon_slov[el].format(c, ", ".join(map(str, fl['spis_del_po_date'][key]["app"][el])))
                c += 1
            if fl['spis_del_po_date'][key]["com"] != ["Нет дефектов"] and fl['spis_del_po_date'][key][
                "com"] != [] and \
                    fl['spis_del_po_date'][key][
                        "com"] != ["Нет дефектов"]:
                k += shablon_slov['com'].format(c, ", ".join(map(str, fl['spis_del_po_date'][key]["com"])))
                c += 1
            pol1 = "Водитель:" + fl['spis_del_po_date'][key]["driver"] + "\n"
            if t != lr:
                mas_message.append(sl)
                lr = t
                sl = t + "\n" + pol1 + k
            else:
                lr = t
                if k != '':
                    if pol1 not in sl:
                        sl += pol1 + k
                    else:
                        stp = k.split("\n")
                        i = 0
                        st = [i[1:] for i in k.split("\n")]
                        for elem in st:
                            if elem not in sl:
                                sl += (stp[i] + '\n')
                            i += 1
        mas_message.append(sl)
        for i in mas_message[1:]:
            botman.send_message(message.chat.id, i)
        botman.send_message(message.chat.id,
                            "Введите номера неисправностей, которые выполнены")
        user_state[message.chat.id] = "del"


@botman.message_handler(commands=['zadachi_po_bort'], func=lambda message: (message.chat.id == fl["admin_id"]))
def zadachi_po_bort(message):
    if fl["spis_del_po_date"] == {}:
        botman.send_message(message.chat.id, "Актуальных заявок нет")
    else:
        sl = {}
        c = 0
        sorted_data = dict(sorted(fl["spis_del_po_bort"].items(), key=lambda x: x[0]))
        for key in sorted_data.keys():
            if key.split(":")[0] not in sl.keys():
                sl[key.split(":")[0]] = {}
            for i, vl in fl["spis_del_po_bort"][key]["app"].items():
                if i not in sl[key.split(":")[0]].keys():
                    sl[key.split(":")[0]][i] = []
                    sl[key.split(":")[0]][i].append(vl)
                elif vl not in sl[key.split(":")[0]][i]:
                    sl[key.split(":")[0]][i].append(vl)
            cm = fl["spis_del_po_bort"][key]["com"]
            if "com" not in sl[key.split(":")[0]].keys():
                sl[key.split(":")[0]]['com'] = []
                sl[key.split(":")[0]]["com"].append(cm)
            elif cm not in sl[key.split(":")[0]]["com"]:
                sl[key.split(":")[0]]["com"].append(cm)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for kl in sl.keys():
            item2 = types.KeyboardButton(kl)
            markup.add(item2)
        botman.send_message(message.chat.id,
                            "Чтобы вывести конкретный борт нажмите на кнопку или впишите название",
                            reply_markup=markup)
        user_state[message.chat.id] = "del_po_bort"


@botman.message_handler(commands=['express_app'], func=lambda message: (message.chat.id == fl["admin_id"]))
def express_app(message):
    if fl["urgent_request"] != {}:
        for key in fl["urgent_request"].keys():
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            pol = "Срочная заявка" + '\n'
            pol0 = "Дата:" + key + "\n"
            pol1 = "Водитель:" + fl["urgent_request"][key]["driver"] + "\n"
            pol2 = "Заявка:" + fl["urgent_request"][key]["request"]
            button = types.InlineKeyboardButton(text="Выполнено", callback_data=key)
            keyboard.add(button)
            botman.send_message(fl["admin_id"], pol + pol0 + pol1 + pol2, reply_markup=keyboard)
            user_state[message.chat.id] = "request"
    else:
        botman.send_message(fl["admin_id"], "Срочных заявок нет")


@botman.message_handler(func=lambda message: (message.chat.id == fl["admin_id"]) or proverka(message))
def reply_to_message(message):
    global cel, call_data, call_message, drive_kl, csv_filename, delit
    if message.chat.id not in user_state.keys():
        user_state[message.chat.id] = ""
    elif user_state[message.chat.id] == 'zav_gar':
        if message.text == "373009373":
            fl["admin_id"] = message.chat.id
            save_pols()
            botman.send_message(message.chat.id, "Роль получена", reply_markup=types.ReplyKeyboardRemove())
        else:
            botman.send_message(message.chat.id, "Неверный пароль", reply_markup=types.ReplyKeyboardRemove())

    elif message.chat.id == fl["admin_id"] and message.text in ["Актуальные заявки по дате",
                                                                "Актуальные заявки по бортам"]:
        if fl["spis_del_po_date"] == {}:
            botman.send_message(message.chat.id, "Актуальных заявок нет")
        else:
            if message.text == "Актуальные заявки по дате":
                c = 1
                mas_message = []
                sorted_data = dict(sorted(fl["spis_del_po_date"].items(), key=lambda x: x[0]))
                shablon_slov = {
                    "engine_oil": "{})Уровень масла ДВС:{}\n",
                    "cooling_liquid": "{})Уровень охл.жидкости:{}\n",
                    "GUR_oil": "{})Уровень масла ГУР:{}\n",
                    "bracking_system": "{})Состояние тормозной.жид:{}\n",
                    "adblue_system": "{})Состояние AdBlue жидкости:{}\n",
                    "lighting_system": "{})Наружное освещение:{}\n",
                    "washer_system": "{})Состояние омывателя и щеток С/О:{}\n",
                    "dashboard_system": "{})Наличие неисправностей панели приборов:{}\n",
                    "tires_system": "{})Повреждение шин:{}\n",
                    "com": "{})Наличие ощутимых дефектов:{}\n"
                }
                lr = ''
                sl = ''
                for key in sorted_data.keys():
                    parts = key.split(':')
                    t = ':'.join(parts[:3])
                    k = ''
                    fault = list(filter(lambda x: fl['spis_del_po_date'][key]["app"][x] not in (
                    "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []),
                                        fl['spis_del_po_date'][key]["app"]))
                    for el in fault:
                        if el in ("engine_oil", "cooling_liquid", "GUR_oil", "adblue_system"):
                            if list(fl["spis_del_po_date"].keys()).index(key) != len(
                                    list(fl["spis_del_po_date"].keys())) - 1:
                                index = list(fl["spis_del_po_date"].keys()).index(key)
                                zap = False
                                for kl in list(fl["spis_del_po_date"].keys())[index + 1:]:
                                    if fl["spis_del_po_date"][key]["driver"] == fl["spis_del_po_date"][kl]["driver"]:
                                        faul = list(
                                            filter(lambda x: fl['spis_del_po_date'][kl]["app"][x] not in (
                                                "MAX", "", ["Нет неисправностей"], ["Нет повреждений"],
                                                ["Нет дефектов"], []),
                                                   fl['spis_del_po_date'][kl]["app"]))
                                        if el in faul:
                                            zap = True
                                if zap == False:
                                    k += shablon_slov[el].format(c, fl['spis_del_po_date'][key]["app"][el])
                            else:
                                k += shablon_slov[el].format(c, fl['spis_del_po_date'][key]["app"][el])
                        else:
                            if list(fl["spis_del_po_date"].keys()).index(key) != len(
                                    list(fl["spis_del_po_date"].keys())) - 1:
                                index = list(fl["spis_del_po_date"].keys()).index(key)
                                zap = False
                                for kl in list(fl["spis_del_po_date"].keys())[index + 1:]:
                                    if fl["spis_del_po_date"][key]["driver"] == fl["spis_del_po_date"][kl][
                                        "driver"]:
                                        faul = list(
                                            filter(lambda x: fl['spis_del_po_date'][kl]["app"][x] not in (
                                                "MAX", "", ["Нет неисправностей"], ["Нет повреждений"],
                                                ["Нет дефектов"], []),
                                                   fl['spis_del_po_date'][kl]["app"]))
                                        if el in faul:
                                            zap = True
                                if zap == False:
                                    k += shablon_slov[el].format(c, ", ".join(
                                        map(str, fl['spis_del_po_date'][key]["app"][el])))
                            else:
                                k += shablon_slov[el].format(c, ", ".join(
                                    map(str, fl['spis_del_po_date'][key]["app"][el])))
                        c += 1
                    if fl['spis_del_po_date'][key]["com"] != ["Нет дефектов"] and fl['spis_del_po_date'][key][
                        "com"] != [] and fl['spis_del_po_date'][key][
                        "com"] != ["Нет дефектов"]:
                        k += shablon_slov['com'].format(c,
                                                        ", ".join(map(str, fl['spis_del_po_date'][key]["com"])))
                        c += 1
                    pol1 = "Водитель:" + fl['spis_del_po_date'][key]["driver"] + "\n"
                    if t != lr:
                        mas_message.append(sl)
                        lr = t
                        sl = t + "\n" + pol1 + k
                    else:
                        lr = t
                        if k != '':
                            if pol1 not in sl:
                                sl += pol1 + k
                            else:
                                stp = k.split("\n")
                                i = 0
                                st = [i[1:] for i in k.split("\n")]
                                for elem in st:
                                    if elem not in sl:
                                        sl += (stp[i] + '\n')
                                    i += 1
                mas_message.append(sl)
                for i in mas_message[1:]:
                    botman.send_message(message.chat.id, i)
                botman.send_message(message.chat.id,
                                    "Введите номера неисправностей, которые выполнены")
                user_state[message.chat.id] = "del"
            else:
                sl = {}
                c = 0
                sorted_data = dict(sorted(fl["spis_del_po_bort"].items(), key=lambda x: x[0]))
                for key in sorted_data.keys():
                    if key.split(":")[0] not in sl.keys():
                        sl[key.split(":")[0]] = {}
                    for i, vl in fl["spis_del_po_bort"][key]["app"].items():
                        if i not in sl[key.split(":")[0]].keys():
                            sl[key.split(":")[0]][i] = []
                            sl[key.split(":")[0]][i].append(vl)
                        elif vl not in sl[key.split(":")[0]][i]:
                            sl[key.split(":")[0]][i].append(vl)
                    cm = fl["spis_del_po_bort"][key]["com"]
                    if "com" not in sl[key.split(":")[0]].keys():
                        sl[key.split(":")[0]]['com'] = []
                        sl[key.split(":")[0]]["com"].append(cm)
                    elif cm not in sl[key.split(":")[0]]["com"]:
                        sl[key.split(":")[0]]["com"].append(cm)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                for kl in sl.keys():
                    item2 = types.KeyboardButton(kl)
                    markup.add(item2)
                botman.send_message(message.chat.id, "Чтобы вывести конкретный борт нажмите на кнопку",
                                    reply_markup=markup)
                user_state[message.chat.id] = "del_po_bort"
    elif user_state[message.chat.id] == "del":
        cel = list(map(int, message.text.split(",")))
        user_state[message.chat.id] = "control"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton("Да")
        item3 = types.KeyboardButton("Нет")
        markup.add(item2, item3)
        botman.send_message(message.chat.id, "Подвердите свой выбор", reply_markup=markup)

    elif user_state[message.chat.id] == "control":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton("Актуальные заявки по дате")
        item3 = types.KeyboardButton("Актуальные заявки по бортам")
        markup.add(item2, item3)
        if message.text == "Да":
            count = 1
            sorted_data = dict(sorted(fl["spis_del_po_date"].items(), key=lambda x: x[0]))
            for key in sorted_data.keys():
                fault = list(filter(lambda x: fl['spis_del_po_date'][key]["app"][x] not in (
                    "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []),
                                    fl['spis_del_po_date'][key]["app"]))
                for el in fault:
                    if count in cel:
                        if el in ("engine_oil", "cooling_liquid", "GUR_oil", "adblue_system"):
                            for kl in sorted_data.keys():
                                if fl['spis_del_po_date'][key]['driver'] == fl['spis_del_po_date'][kl][
                                    'driver']:
                                    csv_mass = [datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"),
                                                fl['spis_del_po_date'][kl]['driver'],
                                                (fl['spis_del_po_date'][kl]["app"][el], "-выполнено")]
                                    fl['spis_del_po_date'][kl]["app"][el] = "MAX"
                                    dr = fl['spis_del_po_date'][kl]['driver'] +":"+ kl
                                    fl['spis_del_po_bort'][dr]["app"][el] = "MAX"
                                    with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                                        writer = csv.writer(file)
                                        writer.writerow(csv_mass)

                        else:
                            csv_mass = [datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"),
                                        fl['spis_del_po_date'][key]['driver'],
                                        (fl['spis_del_po_date'][key]["app"][el], "-выполнено")]
                            fl['spis_del_po_date'][key]["app"][el] = ["Нет неисправностей"]
                            dr = fl['spis_del_po_date'][key]['driver'] +":"+ key
                            fl['spis_del_po_bort'][dr]["app"][el] = ["Нет неисправностей"]
                            with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                                writer = csv.writer(file)
                                writer.writerow(csv_mass)
                    count += 1

                if fl['spis_del_po_date'][key]["com"] != ["Нет дефектов"] and fl['spis_del_po_date'][key][
                    "com"] != [] and fl['spis_del_po_date'][key]["com"] != ["Нет дефектов"] and \
                        fl['spis_del_po_date'][key][
                            "com"] != ["Нет дефектов"]:
                    if count in cel:
                        fl['spis_del_po_date'][key]["com"] = ["Нет дефектов"]
                        dr = fl['spis_del_po_date'][key]['driver'] + key
                        csv_mass = [datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"),
                                    fl['spis_del_po_date'][key]['driver'],
                                    (fl['spis_del_po_date'][key]["com"], "-выполнено")]
                        fl['spis_del_po_bort'][dr]["app"][el] = ["Нет дефектов"]
                        with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                            writer = csv.writer(file)
                            writer.writerow(csv_mass)
                    count += 1
            save_pols()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item2 = types.KeyboardButton("Актуальные заявки по дате")
            item3 = types.KeyboardButton("Актуальные заявки по бортам")
            markup.add(item2, item3)

            botman.send_message(message.chat.id, "Удаление выполнено", reply_markup=markup)

        else:
            botman.send_message(message.chat.id, "Удаление отменено", reply_markup=markup)
        user_state[message.chat.id] = ""

    elif user_state[message.chat.id] == "podtver":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton("Актуальные заявки по дате")
        item3 = types.KeyboardButton("Актуальные заявки по бортам")
        markup.add(item2, item3)
        if message.text == "Да":
            if call_data in fl["spis_del_po_date"].keys():
                dr = fl["spis_del_po_date"][call_data]['driver'] + ":" + call_data
                write_csv_data_vup(csv_filename, fl["spis_del_po_date"][call_data],
                                   datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"))
                del fl["spis_del_po_date"][call_data]
                del fl["spis_del_po_bort"][dr]
                save_pols()
                botman.send_message(message.chat.id, "Заявка выполнена", reply_markup=markup)
                botman.delete_message(message.chat.id, call_message)
            else:
                for key in list(fl["spis_del_po_date"].keys()):
                    if fl["spis_del_po_date"][key]["driver"] == call_data:
                        dr = call_data + ":" + key
                        write_csv_data_vup(csv_filename, fl["spis_del_po_date"][key],
                                           datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"))
                        del fl["spis_del_po_date"][key]
                        del fl["spis_del_po_bort"][dr]
                save_pols()
                botman.send_message(message.chat.id, "Заявка выполнена", reply_markup=markup)
                botman.delete_message(message.chat.id, call_message)

        else:
            botman.send_message(message.chat.id, "Удаление отменено", reply_markup=markup)
        user_state[message.chat.id] = ""

    elif user_state[message.chat.id] == "del_po_bort":
        sl = {}
        c = 1
        shablon_slov = {
            "engine_oil": "{})Уровень масла ДВС:{}\n",
            "cooling_liquid": "{})Уровень охл.жидкости:{}\n",
            "GUR_oil": "{})Уровень масла ГУР:{}\n",
            "bracking_system": "{})Состояние тормозной.жид:{}\n",
            "adblue_system": "{})Состояние AdBlue жидкости:{}\n",
            "lighting_system": "{})Наружное освещение:{}\n",
            "washer_system": "{})Состояние омывателя и щеток С/О:{}\n",
            "dashboard_system": "{})Наличие неисправностей панели приборов:{}\n",
            "tires_system": "{})Повреждение шин:{}\n",
            "com": "{})Наличие ощутимых дефектов:{}\n"
        }
        sorted_data = dict(sorted(fl["spis_del_po_bort"].items(), key=lambda x: x[0]))
        for key in sorted_data.keys():
            if key.split(":")[0] not in sl.keys():
                sl[key.split(":")[0]] = {}
            for i, vl in fl["spis_del_po_bort"][key]["app"].items():
                if i not in sl[key.split(":")[0]].keys():
                    sl[key.split(":")[0]][i] = []
                    sl[key.split(":")[0]][i].append(vl)
                elif vl not in sl[key.split(":")[0]][i]:
                    sl[key.split(":")[0]][i].append(vl)
            cm = fl["spis_del_po_bort"][key]["com"]
            if "com" not in sl[key.split(":")[0]].keys():
                sl[key.split(":")[0]]['com'] = []
                sl[key.split(":")[0]]["com"].append(cm)
            elif cm not in sl[key.split(":")[0]]["com"]:
                sl[key.split(":")[0]]["com"].append(cm)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        k = ''
        fault = list(filter(lambda x: any(index not in (
            "MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"], []) for index in
                                          sl[message.text][x]), sl[message.text]))
        for el in fault:
            neispr = []
            for i in sl[message.text][el]:
                if i not in ("MAX", "", ["Нет неисправностей"], ["Нет повреждений"], ["Нет дефектов"],
                             []) and i not in neispr:
                    neispr.append(i)
            if el in ("engine_oil", "cooling_liquid", "GUR_oil", "adblue_system"):
                k += shablon_slov[el].format(c, ", ".join(map(str, neispr)))
            else:
                k += shablon_slov[el].format(c, ", ".join(map(str, *neispr)))
            c += 1
        st = message.text + "\n" + k
        button = types.InlineKeyboardButton(text="Выполнено", callback_data=message.text)
        keyboard.add(button)
        botman.send_message(message.chat.id, st, reply_markup=keyboard)
        # bracking = [", ".join(i) for i in sl[message.text]["bracking_system"]]
        # pol4 = "4)Состояние тормозной.жид:" + ", ".join(
        #     map(str, bracking)) + "\n"
        # if len(sl[message.text]["adblue_system"]) > 1 and "MAX" in sl[message.text]["adblue_system"]:
        #     AdBlue = "Ниже нормы"
        # else:
        #     AdBlue = "".join(sl[message.text]["adblue_system"])
        # pol5 = "5)Состояние AdBlue жидкости:" + AdBlue + "\n"
        # light = [", ".join(i) for i in sl[message.text]["lighting_system"]]
        # pol6 = "6)Наружное освещение:" + ", ".join(map(str, light)) + "\n"
        # omuv = [", ".join(i) for i in sl[message.text]["washer_system"]]
        # pol7 = "7)Состояние омывателя и щеток С/О:" + ", ".join(
        #     map(str, omuv)) + "\n"
        # dashboard = [", ".join(i) for i in sl[message.text]["dashboard_system"]]
        # pol8 = "8)Наличие неисправностей панели приборов:" + ", ".join(
        #     map(str, dashboard)) + "\n"
        # tires = [", ".join(i) for i in sl[message.text]["tires_system"]]
        # pol9 = "9)Повреждение шин:" + ", ".join(map(str, tires)) + "\n"
        # defk = [", ".join(i) for i in sl[message.text]["com"]]
        # pol10 = "10)Наличие ощутимых дефектов:" + ", ".join(map(str, defk))
        # pol11 = "Водитель:" + message.text + "\n"
        # p = [pol11, pol1, pol2, pol3, pol4, pol5, pol6, pol7, pol8, pol9, pol10]
        # se = ''
        # for pl in p:
        #     if pl.find(":") != len(pl) - 1:
        #         if pl.split(":")[1] not in ["Нет неисправностей\n", "Нет дефектов\n", "Нет повреждений\n", "\n",
        #                                     "MAX\n", "Нет неисправностей, \n", "Нет дефектов, \n",
        #                                     "Нет повреждений, \n"]:
        #             for g in ["Нет неисправностей, ", "Нет дефектов, ",
        #                                     "Нет повреждений, ","Нет неисправностей", "Нет дефектов", "Нет повреждений",
        #                                     "MAX"]:
        #                 pl = pl.replace(g,"",1)
        #             se += pl


    elif user_state[message.chat.id] == "request":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item2 = types.KeyboardButton("Актуальные заявки по дате")
        item3 = types.KeyboardButton("Актуальные заявки по бортам")
        markup.add(item2, item3)
        if message.text == "Да":
            csv_mass = [datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S"),
                        fl['urgent_request'][call_data]["driver"],
                        (fl['urgent_request'][call_data]["request"] + "-выполнено")]
            with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file)
                writer.writerow(csv_mass)
            del fl['urgent_request'][call_data]
            save_pols()
            bot.send_message(message.chat.id, "Заявка выполнена", reply_markup=markup)
            bot.delete_message(message.chat.id, call_message)
        else:
            botman.send_message(message.chat.id, "Удаление отменено", reply_markup=markup)
        user_state[message.chat.id] = ""

    else:
        botman.send_message(message.chat.id, "Команда не распознана")

@bot.message_handler(commands=['settings'])
def settings(message):
    user_state[message.chat.id] = "set"
    bot.send_message(message.chat.id, "Заполните данные сначала")
    bot.send_message(message.chat.id, "Введите гос.номер:")

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id in fl["allowed_users"]:
        # if message.chat.id in user_app.keys():
        #     show_dopoln(message)
        if str(message.chat.id) in users.keys():
            date = ":::"
            for kl in fl['spis_del_po_date'].keys():
                if kl > date and users[str(message.chat.id)]["driver"]== fl['spis_del_po_date'][kl]["driver"]:
                    date = kl

            if date.split(":")[:3] == datetime.datetime.now().strftime("%Y:%m:%d").split(":"):
                user_app[message.chat.id] = {
                    "app": {
                        "engine_oil": "",
                        "cooling_liquid": "",
                        "GUR_oil": "",
                        "bracking_system": [],
                        "adblue_system": '',
                        "lighting_system": [],
                        "washer_system": [],
                        "dashboard_system": [],
                        "tires_system": []
                    },
                    "com": [],
                    "date": ""
                }
                user_app[message.chat.id]["date"] = date
                user_app[message.chat.id]["app"] = fl['spis_del_po_date'][date]["app"]
                user_app[message.chat.id]["com"] = fl['spis_del_po_date'][date]["com"]
                bot.send_message(message.chat.id,
                                 "Чтобы дополнить анкету введите номер поля, которое нужно изменить",
                                 reply_markup=types.ReplyKeyboardRemove())
                show_dopoln(message)
            else:
                user_app[message.chat.id] = {
                    "app": {
                        "engine_oil": "",
                        "cooling_liquid": "",
                        "GUR_oil": "",
                        "bracking_system": [],
                        "adblue_system": '',
                        "lighting_system": [],
                        "washer_system": [],
                        "dashboard_system": [],
                        "tires_system": []
                    },
                    "com": [],
                    "date": ""
                }
                show_keyboard(message.chat.id)
        else:
            user_app[message.chat.id] = {
                "app": {
                    "engine_oil": "",
                    "cooling_liquid": "",
                    "GUR_oil": "",
                    "bracking_system": [],
                    "adblue_system": '',
                    "lighting_system": [],
                    "washer_system": [],
                    "dashboard_system": [],
                    "tires_system": []
                },
                "com": [],
                "date": ""
            }
            show_keyboard(message.chat.id)
    else:
        show_rol_avt(message)


@bot.message_handler(commands=['urgent_request'], func=lambda message: (message.chat.id in fl["allowed_users"]))
def urgent_request(message):
    global drive_kl

    if str(message.chat.id) not in users.keys():
        bot.send_message(message.chat.id, "Для отправления заявки заполните анкету пользователя")
        bot.send_message(message.chat.id, "Введите гос.номер:")
        user_state[message.chat.id] = "driver"
        drive_kl = True
        users[str(message.chat.id)] = {
            "gos_nomer": "",
            "driver": '',
            "probeg": "0"
        }
    else:
        bot.send_message(message.chat.id, "Введите срочную заявку", reply_markup=types.ReplyKeyboardRemove())
        user_state[message.chat.id] = "urgent_request"


@bot.message_handler(func=lambda message: (message.chat.id in fl["allowed_users"]) or proverka(message))
def reply_to_message(message):
    global cel, call_data, call_message, drive_kl, csv_filename,klych
    if message.chat.id not in user_state.keys():
        user_state[message.chat.id] = ""
    if message.text == "Заполнить карту ежедневного осмотра":
        user_app[message.chat.id] = {
            "app": {
                "engine_oil": "",
                "cooling_liquid": "",
                "GUR_oil": "",
                "bracking_system": [],
                "adblue_system": '',
                "lighting_system": [],
                "washer_system": [],
                "dashboard_system": [],
                "tires_system": []
            },
            "com": [],
            "date": ""
        }

        if str(message.chat.id) not in users:
            users[str(message.chat.id)] = {
                "gos_nomer": "",
                "driver": '',
                "probeg": "0"
            }
            user_state[message.chat.id] = "driver"
            bot.send_message(message.chat.id, "Введите гос.номер:")
        else:
            if fl["spis_del_po_date"] != {}:
                for kl in fl["spis_del_po_date"].keys():
                    if fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                            fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "MAX" and \
                            fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                        user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                        show_cool(message)
                        break
                    elif fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                            fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" \
                            and fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "MAX" and \
                            fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                        user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                        user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                        show_GUR(message)
                        break
                    elif fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                            fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" \
                            and fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "Ниже нормы" and \
                            fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                        user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                        user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                        user_app[message.chat.id]["app"]["GUR_oil"] = "Ниже нормы"
                        if datetime.datetime.now().day % 5 == 0:
                            show_bracking(message)
                        else:
                            show_lighting(message)
                        break

                else:
                    show_engine(message)
            else:
                show_engine(message)

    elif user_state[message.chat.id] == "urgent_request":
        save_dat = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
        fl["urgent_request"][save_dat] = {}
        fl["urgent_request"][save_dat]["driver"] = users[str(message.chat.id)]["driver"]
        fl["urgent_request"][save_dat]["request"] = message.text
        bot.send_message(message.chat.id, "Заявка отправлена")
        save_pols()
        csv_mass = [save_dat, users[str(message.chat.id)]["driver"], message.text]
        with open(csv_filename, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(csv_mass)
        botman.send_message(fl["admin_id"], "Срочная заявка", reply_markup=types.ReplyKeyboardRemove())
        pol0 = "Дата:" + save_dat + "\n"
        pol1 = "Водитель:" + users[str(message.chat.id)]["driver"] + "\n"
        pol2 = "Заявка:" + message.text
        botman.send_message(fl["admin_id"], pol0 + pol1 + pol2)
        user_state[message.chat.id] = ""

    elif user_state[message.chat.id] == 'set':
        if str(message.chat.id) not in users[str(message.chat.id)].keys():
            users[str(message.chat.id)] = {
                "gos_nomer": "",
                "driver": '',
                "probeg": "0"
            }
        users[str(message.chat.id)]["gos_nomer"] = message.text
        bot.send_message(message.chat.id, "Введите ФИО:")
        user_state[message.chat.id] = "updater"

    elif user_state[message.chat.id] == "updater":
        users[str(message.chat.id)]["driver"] = message.text
        show_update_keyboard(message)
        klych = True

    elif user_state[message.chat.id] == 'car':
        if message.text == "373373373":
            fl["allowed_users"].append(message.chat.id)
            save_pols()
            bot.send_message(message.chat.id, "Роль получена", reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Неверный пароль", reply_markup=types.ReplyKeyboardRemove())

    elif user_state[message.chat.id] == "driver":
        users[str(message.chat.id)]["gos_nomer"] = message.text
        bot.send_message(message.chat.id, "Введите ФИО:")
        user_state[message.chat.id] = "update"

    elif user_state[message.chat.id] == "update":
        users[str(message.chat.id)]["driver"] = message.text
        show_update_keyboard(message)

    elif user_state[message.chat.id] == "correction":
        if message.text == "Да":
            save_users()
            if klych ==True:
                user_state[message.chat.id] = ""
                klych = False
                bot.send_message(message.chat.id, "Данные откорректированы",
                                 reply_markup=types.ReplyKeyboardRemove())
            elif drive_kl == True:
                user_state[message.chat.id] = "urgent_request"
                drive_kl = False
                bot.send_message(message.chat.id, "Введите текст срочной заявки",
                                 reply_markup=types.ReplyKeyboardRemove())
            else:
                if fl["spis_del_po_date"] != {}:
                    for kl in fl["spis_del_po_date"].keys():
                        if fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "MAX" and \
                                fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                            user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                            show_cool(message)
                            break
                        elif fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" \
                                and fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "MAX" and \
                                fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                            user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                            user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                            show_GUR(message)
                            break
                        elif fl["spis_del_po_date"][kl]["app"]["engine_oil"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" \
                                and fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                            user_app[message.chat.id]["app"]["engine_oil"] = "Ниже нормы"
                            user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                            user_app[message.chat.id]["app"]["GUR_oil"] = "Ниже нормы"
                            if datetime.datetime.now().day % 5 == 0:
                                show_bracking(message)
                            else:
                                show_lighting(message)
                            break

                    else:
                        show_engine(message)
                else:
                    show_engine(message)

        else:
            user_state[message.chat.id] = "driver"
            bot.send_message(message.chat.id, "Заполните данные сначала")
            bot.send_message(message.chat.id, "Введите гос.номер:")
    elif user_state[message.chat.id] == "engine_oil":
        if message.text in ["MAX", "Ниже нормы"]:
            if user_app[message.chat.id]["app"]["engine_oil"] == "":
                user_app[message.chat.id]["app"]["engine_oil"] = message.text
                if fl["spis_del_po_date"] != {}:
                    for kl in fl["spis_del_po_date"].keys():
                        if fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                            user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                            user_app[message.chat.id]["app"]["GUR_oil"] = "Ниже нормы"
                            if datetime.datetime.now().day % 5 == 0:
                                show_bracking(message)
                            else:
                                show_lighting(message)
                            break
                        elif fl["spis_del_po_date"][kl]["app"]["cooling_liquid"] == "Ниже нормы" and \
                                fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "MAX" and \
                                fl["spis_del_po_date"][kl]["driver"] == users[str(message.chat.id)]["driver"]:
                            user_app[message.chat.id]["app"]["cooling_liquid"] = "Ниже нормы"
                            show_GUR(message)
                            break
                    else:
                        show_cool(message)
                else:
                    show_cool(message)
            else:
                user_app[message.chat.id]["app"]["engine_oil"] = message.text
                show_dopoln(message)
        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_engine(message)

    elif user_state[message.chat.id] == "cooling_liquid":
        if message.text in ["MAX", "Ниже нормы"]:
            if user_app[message.chat.id]["app"]["cooling_liquid"] == "":
                user_app[message.chat.id]["app"]["cooling_liquid"] = message.text
                if fl["spis_del_po_date"] != {}:
                    for kl in fl["spis_del_po_date"].keys():
                        if fl["spis_del_po_date"][kl]["app"]["GUR_oil"] == "Ниже нормы":
                            user_app[message.chat.id]["app"]["GUR_oil"] = "Ниже нормы"
                            if datetime.datetime.now().day % 5 == 0:
                                show_bracking(message)
                            else:
                                show_lighting(message)
                            break
                    else:
                        show_GUR(message)
                else:
                    show_GUR(message)
            else:
                user_app[message.chat.id]["app"]["cooling_liquid"] = message.text
                show_dopoln(message)
        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_cool(message)

    elif user_state[message.chat.id] == "GUR_oil":
        if message.text in ["MAX", "Ниже нормы"]:
            if user_app[message.chat.id]["app"]["GUR_oil"] == "":
                user_app[message.chat.id]["app"]["GUR_oil"] = message.text
                if datetime.datetime.now().day % 5 == 0:
                    show_bracking(message)
                else:
                    show_lighting(message)
            else:
                user_app[message.chat.id]["app"]["GUR_oil"] = message.text
                show_dopoln(message)
        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_GUR(message)
    elif user_state[message.chat.id] == "bracking_system":
        if message.text == "Нет дефектов":
            if user_app[message.chat.id]["app"]["bracking_system"] == []:
                user_app[message.chat.id]["app"]["bracking_system"].append(message.text)
                show_dashboard(message)
            else:
                user_app[message.chat.id]["app"]["bracking_system"].append(message.text)
                show_dopoln(message)
        elif message.text == "Дефект":
            bot.send_message(message.chat.id, "Уточните дефект")
            user_state[message.chat.id] = "bracking_problem"

        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_washer(message)
    elif user_state[message.chat.id] == "bracking_problem":
        if user_app[message.chat.id]["app"]["bracking_system"] == []:
            user_app[message.chat.id]["app"]["bracking_system"].append(message.text)
            show_dashboard(message)
        else:
            if "Нет дефектов" in user_app[message.chat.id]["app"]["bracking_system"]:
                user_app[message.chat.id]["app"]["bracking_system"].remove(message.text)
            user_app[message.chat.id]["app"]["bracking_system"].append(message.text)
            show_dopoln(message)

    elif user_state[message.chat.id] == "adblue_system":
        if message.text in ["MAX", "Ниже нормы"]:
            if user_app[message.chat.id]["app"]["adblue_system"] == '':
                user_app[message.chat.id]["app"]["adblue_system"] = message.text
                show_lighting(message)
            else:
                user_app[message.chat.id]["app"]["adblue_system"] = message.text
                show_dopoln(message)
        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_adblue(message)
    elif user_state[message.chat.id] == "lighting_system":
        if message.text == "Нет неисправностей":
            if user_app[message.chat.id]["app"]["lighting_system"] == []:
                user_app[message.chat.id]["app"]["lighting_system"].append(message.text)
                if datetime.datetime.now().day % 2 == 0:
                    show_washer(message)
                else:
                    show_dashboard(message)
            else:
                user_app[message.chat.id]["app"]["lighting_system"].append(message.text)
                show_dopoln(message)
        elif message.text == "Неисправность":
            bot.send_message(message.chat.id, "Уточните неисправность")
            user_state[message.chat.id] = "lighting_problem"

        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_lighting(message)

    elif user_state[message.chat.id] == "lighting_problem":

        if user_app[message.chat.id]["app"]["lighting_system"] == []:
            user_app[message.chat.id]["app"]["lighting_system"].append(message.text)
            if datetime.datetime.now().day % 2 == 0:
                show_washer(message)
            else:
                show_dashboard(message)
        else:
            if "Нет неисправностей" in user_app[message.chat.id]["app"]["lighting_system"]:
                user_app[message.chat.id]["app"]["lighting_system"].remove()
            user_app[message.chat.id]["app"]["lighting_system"].append(message.text)
            show_dopoln(message)
    elif user_state[message.chat.id] == "washer_system":
        if message.text == "Нет неисправностей":
            if user_app[message.chat.id]["app"]["washer_system"] == []:
                user_app[message.chat.id]["app"]["washer_system"].append(message.text)
                show_dashboard(message)
            else:
                user_app[message.chat.id]["app"]["washer_system"].append(message.text)
                show_dopoln(message)
        elif message.text == "Неисправность":
            bot.send_message(message.chat.id, "Уточните неисправность")
            user_state[message.chat.id] = "washer_problem"

        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_washer(message)
    elif user_state[message.chat.id] == "washer_problem":
        if user_app[message.chat.id]["app"]["washer_system"] == []:
            user_app[message.chat.id]["app"]["washer_system"].append(message.text)
            show_dashboard(message)
        else:
            if "Нет неисправностей" in user_app[message.chat.id]["app"]["washer_system"]:
                user_app[message.chat.id]["app"]["washer_system"].remove(message.text)
            user_app[message.chat.id]["app"]["washer_system"].append(message.text)
            show_dopoln(message)
    elif user_state[message.chat.id] == "dashboard_system":
        if message.text == "Нет неисправностей":
            if user_app[message.chat.id]["app"]["dashboard_system"] == []:
                user_app[message.chat.id]["app"]["dashboard_system"].append(message.text)
                show_tires(message)
            else:
                user_app[message.chat.id]["app"]["dashboard_system"].append(message.text)
                show_dopoln(message)

        elif message.text == "Неисправность":
            bot.send_message(message.chat.id, "Уточните неисправность")
            user_state[message.chat.id] = "dashboard_problem"

        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_dashboard(message)
    elif user_state[message.chat.id] == "dashboard_problem":
        if user_app[message.chat.id]["app"]["dashboard_system"] == []:
            user_app[message.chat.id]["app"]["dashboard_system"].append(message.text)
            show_tires(message)
        else:
            if "Нет неисправностей" in user_app[message.chat.id]["app"]["dashboard_system"]:
                user_app[message.chat.id]["app"]["dashboard_system"].remove("Нет неисправностей")
            user_app[message.chat.id]["app"]["dashboard_system"].append(message.text)
            show_dopoln(message)
    elif user_state[message.chat.id] == "tires_system":
        if message.text == "Нет повреждений":
            if user_app[message.chat.id]["app"]["tires_system"] == []:
                user_app[message.chat.id]["app"]["tires_system"].append(message.text)
                show_problem(message)
            else:
                user_app[message.chat.id]["app"]["tires_system"].append(message.text)
                show_dopoln(message)
        elif message.text == "Повреждение":
            bot.send_message(message.chat.id, "Уточните повреждение")
            user_state[message.chat.id] = "tires_problem"

        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_tires(message)
    elif user_state[message.chat.id] == "tires_problem":
        if user_app[message.chat.id]["app"]["tires_system"] == []:
            user_app[message.chat.id]["app"]["tires_system"].append(message.text)
            show_problem(message)
        else:
            if "Нет повреждений" in user_app[message.chat.id]["app"]["tires_system"]:
                user_app[message.chat.id]["app"]["tires_system"].remove("Нет повреждений")
            user_app[message.chat.id]["app"]["tires_system"].append(message.text)
            show_dopoln(message)

    elif user_state[message.chat.id] == "problem_system":
        if message.text == "Нет дефектов":
            if user_app[message.chat.id]["date"] == "":
                user_app[message.chat.id]["com"].append(message.text)
                show_probeg(message)
            else:
                user_app[message.chat.id]["com"].append(message.text)
                show_dopoln(message)
        elif message.text == "Дефект":
            bot.send_message(message.chat.id, "Уточните дефект")
            user_state[message.chat.id] = "problem"
        else:
            bot.send_message(message.chat.id, "Данные введены некорректно")
            show_problem(message)
    elif user_state[message.chat.id] == "problem":
        if "Нет дефектов" in user_app[message.chat.id]["com"]:
            user_app[message.chat.id]["com"].remove("Нет дефектов")
        user_app[message.chat.id]["com"].append(message.text)
        if user_app[message.chat.id]["date"] == "":
            show_probeg(message)
        else:
            show_dopoln(message)
    elif user_state[message.chat.id] == "probeg_system":
        if int(message.text) <= int(users[str(message.chat.id)]["probeg"]):
            bot.send_message(message.chat.id, "Введите корректный пробег")
        else:
            users[str(message.chat.id)]['probeg'] = message.text
            bot.send_message(message.chat.id, "Карта заполнена")
            save_users()
            user_app[message.chat.id]["date"] = datetime.datetime.now().strftime("%Y:%m:%d:%H:%M:%S")
            bot.send_message(message.chat.id,
                             "Чтобы дополнить анкету введите номер поля, которое нужно изменить",
                             reply_markup=types.ReplyKeyboardRemove())
            show_dopoln(message)

    elif user_state[message.chat.id] == "dopoln":
        try:
            sel = int(message.text)
            process_user_input(message, sel)
        except:
            bot.send_message(message.chat.id, "Необходимо ввести номер поля")

    else:
        bot.send_message(message.chat.id, "Команда не распознана")


@botman.callback_query_handler(func=lambda call: True)
def callback_query(call):
    global call_data, call_message
    call_data = call.data
    call_message = call.message.message_id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item2 = types.KeyboardButton("Да")
    item3 = types.KeyboardButton("Нет")
    markup.add(item2, item3)
    botman.send_message(call.message.chat.id, "Подвердите свой выбор", reply_markup=markup)
    if user_state[call.message.chat.id] == "request":
        pass
    elif call_data in fl["urgent_request"].keys():
        user_state[call.message.chat.id] = "request"
    else:
        user_state[call.message.chat.id] = "podtver"

thread1.start()
bot.polling(none_stop=True)
    # except Exception:
    #     continue


