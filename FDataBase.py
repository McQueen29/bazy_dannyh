import sqlite3
class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def addUser(self, name, surname, email, password_hash):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM client WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            self.__cur.execute("INSERT INTO client VALUES(NULL, ?, ?, ?, ?)", (name, surname, email, password_hash))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД " + str(e))
            return False
        return True

    def addOrder(self, id_client, id_tovar, adress, title, price):
        try:
            self.__cur.execute("INSERT INTO orders (id_client, id_tovar, addres, title, price) VALUES(?, ?, ?, ?, ?)", (id_client, id_tovar, adress, title, price))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления заказа в БД  " + str(e))
            return False
        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM client WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных их БД" + str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM client WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return False

    def getCatalog(self):
        try:
            self.__cur.execute(f"SELECT * FROM tovary")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return []

    def getColors(self):
        try:
            self.__cur.execute(f"SELECT * FROM colors")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return []

    def getAppointment(self):
        try:
            self.__cur.execute(f"SELECT * FROM appointments")
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return []

    def getTovar(self, id):
        try:
            self.__cur.execute(f'SELECT tovary.title, types.name AS type_name, tovary.characterisrics, tovary.price FROM tovary '
                               f'JOIN types ON tovary.type = types.id_type WHERE tovary.id_tovara = {id} ')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return []

    def getOrders(self, id_client):
        try:
            self.__cur.execute(f'SELECT id_order, addres, title, price FROM orders WHERE orders.id_client = {id_client} ')
            res = self.__cur.fetchall()
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))

        return []