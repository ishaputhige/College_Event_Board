from flask.globals import session
from flask_session import Session
from flaskext.mysql import MySQL
from flask import Flask, request, render_template, jsonify, flash,redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user,LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import pymysql
from flaskext.mysql import MySQL
import pymysql
from pymysql.cursors import Cursor
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
mysql = MySQL()

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['MYSQL_DATABASE_USER'] = os.environ.get('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('MYSQL_DATABASE_HOST')
mysql.init_app(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
conn = mysql.connect()
cursor = conn.cursor(pymysql.cursors.DictCursor)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        find_user = "SELECT * from registereduser where email = '%s'" % (email)
        cursor.execute(find_user)
        user = cursor.fetchone()
        if user:
            if check_password_hash(user['password'],password):
                flash('Logged in successfully!', category='success')
                print("Loggedin")
                session['user_id']=user['id']
                session['is_club_admin']=user['is_club_admin']
                session['name'] = user['name']
                return redirect('/')
            else:
                print(2)
                flash('Incorrect Password', category='error')
        else:
            print(3)
            flash('Email does not exist, Please Register', category='error')
    return render_template('login.html' )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    find_events = "SELECT * from event"
    cursor.execute(find_events)
    events = cursor.fetchall()
    return render_template('event_description.html',  events = events)

@app.route('/user_events')
def user_events():
    find_events = "select * from event where id in (select event_id from seats where student_id = '%d')" % session['user_id']
    cursor.execute(find_events)
    events = cursor.fetchall()
    return render_template('user_events.html',  events = events)


@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    print(100)
    if session['is_club_admin'] == 1:
        if request.method == 'POST':
            title =  request.form.get('title')
            description = request.form.get('description')
            genre = request.form.get('genre')
            club_name = request.form.get('club-name')
            capacity = request.form.get('capacity')
            location = request.form.get('location')
            date_time = request.form.get('date')
            # check if all the fields are not empty
            insert_event = "INSERT INTO event(id,title,description,genre,location,date_time,club_name,capacity,available,club_admin_id) VALUES (NULL,'%s','%s','%s','%s','%s','%s','%s','%s','%d')" % (title,description,genre,location,date_time,club_name,capacity,capacity,session['user_id'])
            cursor.execute(insert_event)
            conn.commit()
            flash( title + ' is being added', category='success')
            return redirect(url_for('events'))
        else:
            return render_template('new_event.html')
    return redirect(url_for('index'))

@app.route('/book_event/<string:p_id>',methods = ['POST'])
def book_event(p_id):
    print("check")
    check = "select * from seats where event_id = '%s' and student_id = '%d'" % (p_id,session['user_id'])
    cursor.execute(check)
    results = cursor.fetchall()
    print(results)
    if results:
        pass
    else:
        print("Booked")
        book = "Insert into seats values (null,'%s','%d')" % (p_id,session['user_id'])
        cursor.execute(book)
        conn.commit()
        update = "Update event set available = available - 1 where id = '%s'" % (p_id)
        cursor.execute(update)
        conn.commit()
    return redirect('/events')

@app.route('/cancel/<string:p_id>',methods = ['POST'])
def cancel(p_id):
    print("check")
    check = "select * from seats where event_id = '%s' and student_id = '%d'" % (p_id,session['user_id'])
    cursor.execute(check)
    results = cursor.fetchall()
    print("Cancelled")
    cancel = "Delete from seats where event_id= '%s' and student_id = '%d' " % (p_id,session['user_id'])
    cursor.execute(cancel)
    conn.commit()
    update = "Update event set available = available + 1 where id = '%s'" % (p_id)
    cursor.execute(update)
    conn.commit()
    return redirect('/user_events')

@app.route('/club_events')
def club_events():
    find_events = "select * from event where club_admin_id = '%d' " % session['user_id']
    cursor.execute(find_events)
    events = cursor.fetchall()
    return render_template("club_events.html", events=events)

@app.route('/edit_event/<string:p_id>',methods = ['GET','POST'])
def edit_event(p_id):
    print("check")
    event_to_edit= "SELECT * from event where id = '%s'" % (p_id)
    cursor.execute(event_to_edit)
    event_to_edit=cursor.fetchone()
    print(event_to_edit)
    seatsBooked = event_to_edit['capacity']-event_to_edit['available']
    if request.method== 'POST':
        print(1)
        title=request.form['title']
        description=request.form['description']
        genre=request.form['genre']
        location=request.form['location']
        print(1.25)
        date_time=request.form['date']
        print(1.35)
        club_name=request.form['club-name']
        capacity=request.form['capacity']
        available = int(capacity) - int(seatsBooked)
        print(1.5)
        prod_to_update = "UPDATE event SET title = '%s',description = '%s', genre = '%s',location = '%s',date_time = '%s',club_name = '%s',capacity = '%s',available = '%s' where id = '%s'" % (title,description,genre,location,date_time,club_name,capacity,available,p_id)
        cursor.execute(prod_to_update)
        conn.commit()
        print(2)
        return redirect('/club_events')   
    else: 
        return render_template("edit_event.html",result=event_to_edit)



@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        print(1)
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user_type = request.form.get('user_type')
        if password1 != password2:
            print(2)
            flash('Passwords not matching', category='error')
        elif len(name) < 3:
            flash('Name must be more than 2 Characters', category='error')
        else:
            find_user = "SELECT * from registereduser where email = '%s'" % (email)

            cursor.execute(find_user)
            user = cursor.fetchone()
            
            if user:
                print(4)
                flash('Account already exists, Please Login', category='warning')
            else:
                print(5)
                if user_type == "club_admin":
                    new_user = "INSERT into registereduser(id,email,password,name,is_club_admin,is_super_admin) VALUES (NULL,'%s','%s','%s','%d','%d')" % (email,generate_password_hash(password1, method='sha256'),name,1,0)
    
                else:
                    new_user = "INSERT into registereduser(id,email,password,name,is_club_admin,is_super_admin) VALUES (NULL,'%s','%s','%s','%d','%d')" % (email,generate_password_hash(password1, method='sha256'),name,0,0)
                print(new_user)
                cursor.execute(new_user)
                conn.commit()
                return redirect('/login')
                flash('Account created!', category='success')

    return render_template('sign_up.html', user = current_user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)
   
