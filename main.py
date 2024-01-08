from flask import Flask, render_template, request, flash, url_for, session, redirect, g
import sqlite3
import os
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin

DATABASE = '/db/web3.db'
DEBUG = True
SECRET_KEY = 'ferhrdshjgdffsdvsdkfm'

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'web3.db')))
login_manager = LoginManager(app)
login_manager.login_view = 'autorization'
login_manager.login_message = "Вам необходимо авторизоваться"
login_manager.login_message_category = "success"

# ВСЕ ДЛЯ БД
def connect_db(): #подключение к бд
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_db():# подклбчение к БД внутри запроса
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error): # разрыв соединения с БД
    if hasattr(g, 'link_db'):
        g.link_db.close()

dbase = None
@app.before_request
def before_request():
    global dbase
    db = get_db()
    dbase = FDataBase(db)



# ВСЕ ДЛЯ САТЙА
@app.route("/")
def index():
    if current_user.is_authenticated:
        return render_template('main.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('main.html', sing_in="АВТОРИЗАЦИЯ")


@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

@app.route("/autorization", methods=["POST", "GET"])
def autorization():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['password'], request.form['password']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remain') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for('profile'))
        flash("Неверный пароль или логин", "error")

    return render_template('autorization.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for("autorization"))

@app.route('/profile')
@login_required
def profile():
    id_user = current_user.get_id()
    name_user = current_user.get_name()
    surname_user = current_user.get_surname()
    email_user = current_user.get_email()
    if dbase.getOrders(id_user):
        res = dbase.getOrders(id_user)
        return render_template('profile.html', id_user=id_user, name_user=name_user, surname_user=surname_user, email_user=email_user, orders=res)
    return render_template('profile.html', id_user=id_user, name_user=name_user, surname_user=surname_user, email_user=email_user)

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if len(request.form['name']) > 2 and len(request.form['surname']) > 2 \
                and len(request.form['email']) > 10 and request.form['password'] == request.form['password2']:
            hash = generate_password_hash(request.form['password'])
            res = dbase.addUser(request.form['name'], request.form['surname'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегестрированы", "success")
                return redirect(url_for('autorization'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
    return render_template('register.html')

@app.route("/order/<tovar_id>", methods=["POST", "GET"])
@login_required
def order(tovar_id):
    tovar_info = dbase.getTovar(tovar_id)
    id_user = current_user.get_id()
    name_user = current_user.get_name()
    surname_user = current_user.get_surname()
    email_user = current_user.get_email()
    if request.method == "POST":
        address = request.form['address']
        res = dbase.addOrder(id_user, tovar_id, address, tovar_info[0][0], tovar_info[0][-1])
        return redirect(url_for('profile'))
    return render_template('order.html', title_tovar=tovar_info[0][0], type_tovar=tovar_info[0][1], characteristic_tovar=tovar_info[0][2],
                           tovar_price=tovar_info[0][-1], name_user=name_user, surname_user=surname_user, email_user=email_user)

@app.route("/about_us")
def about():
    if current_user.is_authenticated:
        return render_template('about_us.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('about_us.html', sing_in="АВТОРИЗАЦИЯ")

@app.route("/about_us/ekskursii_na_proizvodstvo")
def ekskursii_na_proizvodstvo():
    if current_user.is_authenticated:
        return render_template('ekskursii_na_proizvodstvo.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('ekskursii_na_proizvodstvo.html', sing_in="АВТОРИЗАЦИЯ")

@app.route("/about_us/history")
def history():
    if current_user.is_authenticated:
        return render_template('history.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('history.html', sing_in="АВТОРИЗАЦИЯ")

@app.route("/catalog", methods=["POST", "GET"])
def catalog():
    tovars = dbase.getCatalog()
    colors = dbase.getColors()
    appoint = dbase.getAppointment()
    if current_user.is_authenticated:
        if request.method == "POST":
            email_user = current_user.get_email()
            tovar_id = request.form['tovar_id']
            return redirect(request.args.get("next") or url_for('order', tovar_id=tovar_id))

        return render_template('catalog.html', sing_in='ПРОФИЛЬ', catalog=tovars, color=colors, appoint=appoint)
    else:
        if request.method == "POST":
            return redirect('autorization')
        return render_template('catalog.html', sing_in="АВТОРИЗАЦИЯ", catalog=tovars, color=colors, appoint=appoint)

@app.route("/catalog/syveniry", methods=["POST", "GET"])
def syveniry():
    tovars = dbase.getCatalog()
    colors = dbase.getColors()
    appoint = dbase.getAppointment()
    if current_user.is_authenticated:
        if request.method == "POST":
            email_user = current_user.get_email()
            tovar_id = request.form['tovar_id']
            return redirect(request.args.get("next") or url_for('order', tovar_id=tovar_id))

        return render_template('syveniry.html', sing_in='ПРОФИЛЬ', catalog=tovars, color=colors, appoint=appoint)
    else:
        if request.method == "POST":
            return redirect('autorization')
        return render_template('syveniry.html', sing_in="АВТОРИЗАЦИЯ", catalog=tovars, color=colors, appoint=appoint)

@app.route("/catalog/predmety_int", methods=["POST", "GET"])
def predmety_int():
    tovars = dbase.getCatalog()
    colors = dbase.getColors()
    appoint = dbase.getAppointment()
    if current_user.is_authenticated:
        if request.method == "POST":
            email_user = current_user.get_email()
            tovar_id = request.form['tovar_id']
            return redirect(request.args.get("next") or url_for('order', tovar_id=tovar_id))

        return render_template('predmety_int.html', sing_in='ПРОФИЛЬ', catalog=tovars, color=colors, appoint=appoint)
    else:
        if request.method == "POST":
            return redirect('autorization')
        return render_template('predmety_int.html', sing_in="АВТОРИЗАЦИЯ", catalog=tovars, color=colors, appoint=appoint)

@app.route("/catalog/predmety_serv", methods=["POST", "GET"])
def predmety_serv():
    tovars = dbase.getCatalog()
    colors = dbase.getColors()
    appoint = dbase.getAppointment()
    if current_user.is_authenticated:
        if request.method == "POST":
            email_user = current_user.get_email()
            tovar_id = request.form['tovar_id']
            return redirect(request.args.get("next") or url_for('order', tovar_id=tovar_id))

        return render_template('predmety_serv.html', sing_in='ПРОФИЛЬ', catalog=tovars, color=colors, appoint=appoint)
    else:
        if request.method == "POST":
            return redirect('autorization')
        return render_template('predmety_serv.html', sing_in="АВТОРИЗАЦИЯ", catalog=tovars, color=colors, appoint=appoint)

@app.route("/contacts")
def contacts():
    if current_user.is_authenticated:
        return render_template('contacts.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('contacts.html', sing_in="АВТОРИЗАЦИЯ")

@app.route("/oplata")
def oplata():
    if current_user.is_authenticated:
        return render_template('oplata.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('oplata.html', sing_in="АВТОРИЗАЦИЯ")

@app.route("/shops")
def shops():
    if current_user.is_authenticated:
        return render_template('shops.html', sing_in='ПРОФИЛЬ')
    else:
        return render_template('shops.html', sing_in="АВТОРИЗАЦИЯ")

if __name__ == "__main__":
    app.run(debug=True)