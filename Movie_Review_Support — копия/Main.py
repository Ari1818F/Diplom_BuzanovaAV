from dotenv import load_dotenv
import os
import mysql.connector
import telebot
import hashlib

load_dotenv()

# Внешние переменные
DB_Host = os.getenv("Host_DB")
DB_User = os.getenv("User_DB")
DB_Password = os.getenv("Password_DB")
DB_Name = os.getenv("Name_DB")

TG_Token = os.getenv("TG_Token")

# База данных
def Connect_DB ():
    db = mysql.connector.connect(host=DB_Host, user=DB_User, password=DB_Password, database=DB_Name)

    if db.is_connected():
        return db
    else:
        return None

def Use_DB (db : mysql.connector.connection.MySQLConnection, Qwery : str):
    Cursor = db.cursor()
    Cursor.execute(Qwery)

    if Qwery[0:6].upper() == "SELECT": #SELECT
        Result = Cursor.fetchall()
        Cursor.close()
    
    elif Qwery[0:6].upper() == "INSERT": #INSERT
        db.commit()

        Result = Cursor.lastrowid
        Cursor.close()

    elif Qwery[0:6].upper() in ("UPDATE","DELETE"): #UPDATE и DELETE
        db.commit()

        Result = Cursor.rowcount
        Cursor.close()
    
    else:
        Result = None
        Cursor.close()
    
    return Result

def Close_DB (db : mysql.connector.connection.MySQLConnection):
    db.close()

# Шифрование
def SHA224(data : str):
    return hashlib.sha224(data.encode()).hexdigest()

# Обработка данных
User_Data = {}

def Check_User_Save(Telegram_ID : int):
    if Telegram_ID in User_Data:
        return True
    else:
        return False

def New_User_Save(Telegram_ID : int):
    User_Data[Telegram_ID] = {}

def User_Save_Str (Telegram_ID : int, Name : str, Value : str = ""):
    if Check_User_Save(Telegram_ID):
        Data = User_Data[Telegram_ID]
        Data[Name] = Value
        User_Data[Telegram_ID] = Data

    else:
        New_User_Save(Telegram_ID)
        User_Save_Str(Telegram_ID, Name, Value)

def User_Save_Int (Telegram_ID : int, Name : str, Value : int = 0):
    if Check_User_Save(Telegram_ID):
        Data = User_Data[Telegram_ID]
        Data[Name] = Value
        User_Data[Telegram_ID] = Data

    else:
        New_User_Save(Telegram_ID)
        User_Save_Int(Telegram_ID, Name, Value)

def Check_T_ID (Telegram_ID: int):
    DB = Connect_DB()

    try:
        User_Data = Use_DB(DB, f'Select `Username` from `User` where `Telegram_ID` = {Telegram_ID};')
        User_Data = [User[0] for User in User_Data]

        if not User_Data:
            return False
        
        else:
            return True

    finally:
        Close_DB(DB)

def Check_Authorization (Login : str, Password : str):
    DB = Connect_DB()

    try:
        User_Auth = Use_DB(DB, f'Select `Username` from `User` where `Username` = "{Login}" and `Password` = "{SHA224(Password)}";')
        
        if not User_Auth:
            return False
        else:
            return True

    finally:
        Close_DB(DB)

def Update_User (Telegram_ID: int, Username : str):
    DB = Connect_DB()

    try:
        User_Password = Use_DB(DB, f'UPDATE `User` SET `Telegram_ID` = "{Telegram_ID}" WHERE `User`.`Username` = "{Username}";')

    finally:
        Close_DB(DB)

def Get_Role_User (Telegram_ID: int):
    DB = Connect_DB()

    try:
        User_Role = Use_DB(DB, f'Select `ID_role` from `User` where `Telegram_ID` = {Telegram_ID};')
        User_Role = User_Role[0][0]

        Name_Role = Use_DB(DB, f'Select `Name` from `Role` where `ID` = {User_Role};')
        Name_Role = Name_Role[0][0]

        return Name_Role

    finally:
        Close_DB(DB)

def Get_Name_User (Telegram_ID: int):
    DB = Connect_DB()

    try:
        User_Name = Use_DB(DB, f'Select `Username` from `User` where `Telegram_ID` = {Telegram_ID};')
        User_Name = User_Name[0][0]

        return User_Name

    finally:
        Close_DB(DB)

def Get_ID_User (Telegram_ID: int):
    DB = Connect_DB()

    try:
        User_ID = Use_DB(DB, f'Select `ID` from `User` where `Telegram_ID` = {Telegram_ID};')
        User_ID = User_ID[0][0]

        return User_ID

    finally:
        Close_DB(DB)

def Get_Name_For_ID (ID: int):
    DB = Connect_DB()

    try:
        User_Name = Use_DB(DB, f'Select `Username` from `User` where `ID` = {ID};')
        User_Name = User_Name[0][0]

        return User_Name

    finally:
        Close_DB(DB)

def Get_Request_User (Telegram_ID: int):
    DB = Connect_DB()

    try:
        Data = Use_DB(DB, f'Select * from `Request` where `ID_user` = {Get_ID_User(Telegram_ID)};')

        return Data

    finally:
        Close_DB(DB)

def Get_Request_Users ():
    DB = Connect_DB()

    try:
        Data = Use_DB(DB, f'Select * from `Request` where `ID_status` in (1, 2);')

        return Data

    finally:
        Close_DB(DB)

def Get_Request_Devs ():
    DB = Connect_DB()

    try:
        Data = Use_DB(DB, f'Select * from `Error` where `ID_Work` in (1, 2, 3);')

        return Data

    finally:
        Close_DB(DB)

def Get_Name_Status (ID: int):
    DB = Connect_DB()

    try:
        Name = Use_DB(DB, f'Select `Name` from `Status` where `ID` = {ID};')
        Name = Name[0][0]

        return Name

    finally:
        Close_DB(DB)

def Get_Name_Platform (ID: int):
    DB = Connect_DB()

    try:
        Name = Use_DB(DB, f'Select `Name` from `Platform` where `ID` = {ID};')
        Name = Name[0][0]

        return Name

    finally:
        Close_DB(DB)

def Get_Name_Work (ID: int):
    DB = Connect_DB()

    try:
        Name = Use_DB(DB, f'Select `Name` from `Work` where `ID` = {ID};')
        Name = Name[0][0]

        return Name

    finally:
        Close_DB(DB)

def Insert_Request_User (User_ID : int, Reason : str, Details : str):
    DB = Connect_DB()

    try:
        Use_DB(DB, f"INSERT INTO `Request` (`ID`, `ID_user`, `Reason`, `Details`, `ID_status`) VALUES (NULL, {User_ID}, '{Reason}', '{Details}', 1);")

    finally:
        Close_DB(DB)

def Insert_Request_Dev (User_ID : int, Platform : int, Message : str):
    DB = Connect_DB()

    try:
        Use_DB(DB, f"INSERT INTO `Error` (`ID`, `ID_Support`, `ID_Dev`, `ID_Platform`, `Message`, `ID_Work`) VALUES (NULL, {User_ID}, NULL, {Platform}, '{Message}', 1);")

    finally:
        Close_DB(DB)

def Answer_Request (message : telebot.types.Message):
    Update_Request(User_Data[message.chat.id]['ID_Message'], message.text)
    Bot.send_message(message.chat.id, 
                     "Ответ отправлен пользователю.")

def Answer_ID (message : telebot.types.Message):
    Sent = Bot.send_message(message.chat.id,
                            "Введите ID пользовательской заявки: ")
    Bot.register_next_step_handler(Sent, Answer_ID_1)

def Answer_ID_1 (message : telebot.types.Message):
    User_Save_Int(message.chat.id, "ID_Message", int(message.text))
    
    # Теперь запрашиваем ответ
    Sent = Bot.send_message(message.chat.id,
                            "Напишите ответ пользователю: ")
    Bot.register_next_step_handler(Sent, Answer_Request)

def Update_Request (ID: int, Answer : str):
    DB = Connect_DB()

    try:
        Use_DB(DB, f'UPDATE `Request` SET `Answer` = "{Answer}", `ID_status` = 2 WHERE `Request`.`ID` = {ID};')

    finally:
        Close_DB(DB)

def New_User_Request ():
    DB = Connect_DB()

    try:
        Data = Use_DB(DB, f'Select `ID` from `Request` where `ID_status` = 1;')

        return Data

    finally:
        Close_DB(DB)

# Телеграм-бот
Bot = telebot.TeleBot(TG_Token)

@Bot.message_handler(commands=['start']) # Меню бота
def Start (message : telebot.types.Message):
    if Check_T_ID(message.chat.id):
        if Get_Role_User(message.chat.id) == "Пользователь":
            keyboard = telebot.types.InlineKeyboardMarkup()
            Button_List = telebot.types.InlineKeyboardButton("Ваши заявки", callback_data='Request_List')
            Button_Request = telebot.types.InlineKeyboardButton("Новая заявка", callback_data='Request')
            keyboard.add(Button_List)
            keyboard.add(Button_Request)
            Bot.send_message(message.chat.id,
                     f'Приветствую, {Get_Name_User(message.chat.id)}. Здесь вы можете сообщить об ошибках, которые произошли на сайте или в боте.', reply_markup=keyboard)

        elif Get_Role_User(message.chat.id) in ("Тех. поддержка", "Администратор"):
            # Проверить новые заявки, если есть, то сообщить
            User_Request = New_User_Request()

            if not User_Request:
                Bot.send_message(message.chat.id,
                     f'Новых заявок нет.')
            else:
                Bot.send_message(message.chat.id,
                     f'Есть новые заявки, проверьте список!')

            keyboard = telebot.types.InlineKeyboardMarkup()
            Button_List = telebot.types.InlineKeyboardButton("Ваши заявки", callback_data='Request_List')
            Button_Request = telebot.types.InlineKeyboardButton("Новая заявка", callback_data='Request')
            keyboard.add(Button_List)
            keyboard.add(Button_Request)
            Bot.send_message(message.chat.id,
                     f'Приветствую, {Get_Name_User(message.chat.id)}. Здесь вы можете сообщить об ошибках, которые произошли на сайте или в боте. Роль: {Get_Role_User(message.chat.id)}.', reply_markup=keyboard)

    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        Button_Log = telebot.types.InlineKeyboardButton("Войти", callback_data='Login')
        keyboard.add(Button_Log)
        Bot.send_message(message.chat.id,
                     f'Movie Review Support - техническая поддержка проекта Movie Review в Telegram.', reply_markup=keyboard)

@Bot.message_handler(commands=['log']) # Авторизация
def Auth (message : telebot.types.Message):
    Sent = Bot.send_message(message.chat.id,
                     'Авторизация \nВведите логин:')

    Bot.register_next_step_handler(Sent, Auth_1)

def Auth_1 (message : telebot.types.Message):
    User_Save_Str(message.chat.id, "Auth_Login", message.text)

    Sent = Bot.send_message(message.chat.id,
                     'Авторизация \nВведите пароль:')

    Bot.register_next_step_handler(Sent, Auth_2)

def Auth_2 (message : telebot.types.Message):
    User_Save_Str(message.chat.id, "Auth_Password", message.text)
    Data = User_Data[message.chat.id]

    if Check_Authorization(Data["Auth_Login"], Data["Auth_Password"]):
        Update_User(message.chat.id, Data["Auth_Login"])

        Start(message)
    else:
        Bot.send_message(message.chat.id,
                     f'Неправильно введён логин или пароль!')
        
@Bot.message_handler(commands=['requests']) # Список заявок
def Requests_List (message : telebot.types.Message):
    if Check_T_ID(message.chat.id):
        if Get_Role_User(message.chat.id) == "Пользователь":
            Requests_List_LVL_1(message)

        elif Get_Role_User(message.chat.id) in ("Тех. поддержка", "Администратор"):
            keyboard = telebot.types.InlineKeyboardMarkup()
            Button_List = telebot.types.InlineKeyboardButton("Заявки пользователей", callback_data='Request_LVL_1')
            Button_Request = telebot.types.InlineKeyboardButton("Технические заявки", callback_data='Request_LVL_2')
            keyboard.add(Button_List)
            keyboard.add(Button_Request)
            Bot.send_message(message.chat.id,
                     f'Выберите список заявок:', reply_markup=keyboard)

    else:
        Bot.send_message(message.chat.id,
                     f'Вы не зарегистрированы! Для авторизации используйте /log')
        
def Requests_List_LVL_1 (message : telebot.types.Message):
    if Get_Role_User(message.chat.id) == "Пользователь":
        Data = Get_Request_User(message.chat.id) # Получить записи пользователя

        if len(Data) >= 1:
            for i in range(len(Data)): # Вывести записи пользователя
                if Data[i][5] == "":
                    Bot.send_message(message.chat.id,
                        f'Заявка №{Data[i][0]} \nПричина: {Data[i][2]} \nКомментарий: {Data[i][3]} \nСтатус: {Get_Name_Status(Data[i][4])}')
                else:
                    Bot.send_message(message.chat.id,
                        f'Заявка №{Data[i][0]} \nПричина: {Data[i][2]} \nКомментарий: {Data[i][3]} \nСтатус: {Get_Name_Status(Data[i][4])} \nОтвет: \n{Data[i][5]}')

        else:
            Bot.send_message(message.chat.id,
                     f'Вы ещё не отправляли заявок.')
            
    else:
        Data = Get_Request_Users() # Получить записи пользователя

        if len(Data) >= 1:
            for i in range(len(Data)): # Вывести записи пользователя
                if Data[i][5] == "":
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    Button_Answer = telebot.types.InlineKeyboardButton("Ответить", callback_data='Answer')
                    keyboard.add(Button_Answer)
                    Bot.send_message(message.chat.id,
                        f'Заявка №{Data[i][0]} \nПричина: {Data[i][2]} \nКомментарий: {Data[i][3]} \nСтатус: {Get_Name_Status(Data[i][4])}', 
                        reply_markup=keyboard)
                else:
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    Button_Answer = telebot.types.InlineKeyboardButton("Ответить", callback_data='Answer')
                    keyboard.add(Button_Answer)
                    Bot.send_message(message.chat.id,
                        f'Заявка №{Data[i][0]} \nПричина: {Data[i][2]} \nКомментарий: {Data[i][3]} \nСтатус: {Get_Name_Status(Data[i][4])} \nОтвет: \n{Data[i][5]}', 
                        reply_markup=keyboard)

        else:
            Bot.send_message(message.chat.id,
                     f'Нет заявок.')

def Requests_List_LVL_2 (message : telebot.types.Message):
    Data = Get_Request_Devs()

    if len(Data) >= 1:
        for i in range(len(Data)):
            if Data[i][2] == "NULL":
                Name_Dev = "Не определён"
            else:
                Name_Dev = Get_Name_For_ID(Data[i][2])
            
            Bot.send_message(message.chat.id,
                     f'Заявка №{Data[i][0]} \nНик проверяющего: {Get_Name_For_ID(Data[i][1])} \nНик разработчика: {Name_Dev} \nПлатформа: {Get_Name_Platform(Data[i][3])} \nКомментарий: {Data[i][4]} \nСтатус: {Get_Name_Work(Data[i][5])}')

    else:
        Bot.send_message(message.chat.id,
                     f'Нет заявок.')
        
@Bot.message_handler(commands=['request']) # Новая заявка
def Request (message : telebot.types.Message):
    if Check_T_ID(message.chat.id):
        if Get_Role_User(message.chat.id) in ("Тех. поддержка", "Администратор"):
            keyboard = telebot.types.InlineKeyboardMarkup()
            Button_User = telebot.types.InlineKeyboardButton("Пользовательская заявка", callback_data='User_Request')
            Button_Dev = telebot.types.InlineKeyboardButton("Техническая заявка", callback_data='Dev_Request')
            keyboard.add(Button_User)
            keyboard.add(Button_Dev)
            Bot.send_message(message.chat.id,
                        f'Выберите тип заявки:', reply_markup=keyboard)
            
        else:
            Request_User(message)

    else:
        Bot.send_message(message.chat.id,
                     f'Вы не зарегистрированы! Для авторизации используйте /log')
        
def Request_User (message : telebot.types.Message):
    Sent = Bot.send_message(message.chat.id,
                     f'Заявка: \nВведите краткую причину:')
    
    Bot.register_next_step_handler(Sent, Request_User_1)

def Request_User_1 (message : telebot.types.Message):
    User_Save_Str(message.chat.id, "Reason", message.text)

    Sent = Bot.send_message(message.chat.id,
                     f'Заявка: \nВведите комментарий:')
    
    Bot.register_next_step_handler(Sent, Request_User_2)

def Request_User_2 (message : telebot.types.Message):
    User_Save_Str(message.chat.id, "Details", message.text)

    Data = User_Data[message.chat.id]

    if Data["Reason"] != "":
        Insert_Request_User(Get_ID_User(message.chat.id), Data["Reason"], Data["Details"])
        Bot.send_message(message.chat.id,
                     f'Спасибо за заявку. Мы рассмотрим её и постараемся решить.')

    else:
        Bot.send_message(message.chat.id,
                     f'Причина пуста!')

def Request_Dev (message : telebot.types.Message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    Button_1 = telebot.types.InlineKeyboardButton("Сайт", callback_data='Platform_1')
    Button_2 = telebot.types.InlineKeyboardButton("Telegram-бот MR", callback_data='Platform_2')
    Button_3 = telebot.types.InlineKeyboardButton("Telegram-бот MR Support", callback_data='Platform_3')
    keyboard.add(Button_1)
    keyboard.add(Button_2)
    keyboard.add(Button_3)
    Bot.send_message(message.chat.id,
                     f'Заявка: \nВыберите платформу, на которой произошла ошибка:', reply_markup=keyboard)
    
def Request_Dev_1 (message : telebot.types.Message):
    Sent = Bot.send_message(message.chat.id,
                     f'Заявка: \nВведите комментарий:')
    
    Bot.register_next_step_handler(Sent, Request_Dev_2)

def Request_Dev_2 (message : telebot.types.Message):
    User_Save_Str(message.chat.id, "Message", message.text)

    Data = User_Data[message.chat.id]
    if Data["Message"] != "":
        Insert_Request_Dev(Get_ID_User(message.chat.id), Data["Platform"], Data["Message"])
        Bot.send_message(message.chat.id,
                     f'Спасибо за обработку запросов.')
    
    else:
        Bot.send_message(message.chat.id,
                     f'Комментарий пуст!')

@Bot.message_handler(commands=['creators']) # Создатели
def Creators (message : telebot.types.Message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    Button_Kon = telebot.types.InlineKeyboardButton("Поддержать Konaca", url='https://www.donationalerts.com/r/konaca_')
    Button_Rin = telebot.types.InlineKeyboardButton("Поддержать Rin", url='https://www.donationalerts.com/r/rin128')
    Button_Ari = telebot.types.InlineKeyboardButton("Поддержать Ari", url='https://www.donationalerts.com/r/ari1818f')
    keyboard.add(Button_Kon, Button_Rin)
    keyboard.add(Button_Ari)

    Bot.send_message(message.chat.id,
                     f'Команда сервиса Movie Review: \nKonaca (Влад) - Создатель и программист Telegram-бота \nRin (Марина) - программист сайта \nAri - программист тех. поддержки',
                     reply_markup=keyboard)
    
@Bot.callback_query_handler(func=lambda call: True) # Обработка callback
def Handle_Query(call : telebot.types.CallbackQuery):
    # Функции
    def Handle_Login (call : telebot.types.CallbackQuery):
        Auth(call.message)

    def Handle_Requests_List (call : telebot.types.CallbackQuery):
        Requests_List(call.message)

    def Handle_Request (call : telebot.types.CallbackQuery):
        Request(call.message)

    def Handle_Request_LVL_1 (call : telebot.types.CallbackQuery):
        Requests_List_LVL_1(call.message)

    def Handle_Request_LVL_2 (call : telebot.types.CallbackQuery):
        Requests_List_LVL_2(call.message)

    def Handle_User_Request (call : telebot.types.CallbackQuery):
        Request_User(call.message)

    def Handle_Dev_Request (call : telebot.types.CallbackQuery):
        Request_Dev(call.message)

    def Handle_Platform_1 (call : telebot.types.CallbackQuery):
        User_Save_Int(call.message.chat.id, "Platform", 1)
        Request_Dev_1(call.message)
    
    def Handle_Platform_2 (call : telebot.types.CallbackQuery):
        User_Save_Int(call.message.chat.id, "Platform", 2)
        Request_Dev_1(call.message)
    
    def Handle_Platform_3 (call : telebot.types.CallbackQuery):
        User_Save_Int(call.message.chat.id, "Platform", 3)
        Request_Dev_1(call.message)

    def Handle_Answer (call : telebot.types.CallbackQuery):
        Answer_ID(call.message)

    # Список
    Actions = {
        'Login': lambda Param: Handle_Login(Param),

        'Request_List': lambda Param: Handle_Requests_List(Param),
        'Request': lambda Param: Handle_Request(Param),

        'Request_LVL_1': lambda Param: Handle_Request_LVL_1(Param),
        'Request_LVL_2': lambda Param: Handle_Request_LVL_2(Param),

        'User_Request': lambda Param: Handle_User_Request(Param),
        'Dev_Request': lambda Param: Handle_Dev_Request(Param),

        'Platform_1': lambda Param: Handle_Platform_1(Param),
        'Platform_2': lambda Param: Handle_Platform_2(Param),
        'Platform_3': lambda Param: Handle_Platform_3(Param),

        'Answer': lambda Param: Handle_Answer(Param),
    }
    
    Actions.get(call.data)(call)

Bot.infinity_polling()