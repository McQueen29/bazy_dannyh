from flask_login import UserMixin
class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])

    def get_name(self):
        return str(self.__user['name'])

    def get_surname(self):
        return str(self.__user['surname'])

    def get_email(self):
        return str(self.__user['email'])