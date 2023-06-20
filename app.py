from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
import bcrypt
from datetime import date, datetime, timedelta

import time
import smtplib
import random
import math

app = Flask(__name__)
app.secret_key ='81117add8ab027690bd40297'

conn = sqlite3.connect('covid.db')
conn.execute('PRAGMA foreign_keys = ON;')
cursor = conn.cursor()

cursor.execute('''
 CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email_id TEXT UNIQUE,
        password TEXT,
        ph_no INTEGER,
        otp INTEGER DEFAULT 0,
        status INTEGER DEFAULT 0,
        date DATE
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email_id TEXT UNIQUE,
        password TEXT,
        ph_no INTEGER,
        otp INTEGER DEFAULT 0,
        balance INTEGER DEFAULT 50,
        status INTEGER DEFAULT 0,
        date DATE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vacc_Center (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        place TEXT,
        working_hour INTEGER DEFAULT 10,
        dosage INTEGER DEFAULT 0,
        slots INTEGER DEFAULT 10,
        slot_time_status INTEGER DEFAULT 0,
        slot_vaccine INTEGER DEFAULT 1,
        vaccine_name TEXT,
        date DATE,
        admin_id INTEGER,
        admin_name TEXT,
        FOREIGN KEY (admin_id) REFERENCES Admin(id) ON DELETE CASCADE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Slots (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        center_id INTEGER,
        center_name TEXT,
        user_id INTEGER,
        user_name INTEGER,
        slot_timing_id INTEGER,
        slot_timing TEXT,
        status INTEGER DEFAULT 0,
        date DATE,
        place TEXT,
        email TEXT,
        FOREIGN KEY (center_id) REFERENCES Vacc_Center(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES User(id) ON DELETE CASCADE,
        FOREIGN KEY (slot_timing_id) REFERENCES slots_timing(id) ON DELETE CASCADE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS slots_timing (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        center_id INTEGER,
        center_name TEXT,
        slot_timing TEXT,
        FOREIGN KEY (center_id) REFERENCES Vacc_Center(id) ON DELETE CASCADE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slot_id INTEGER,
        user_id INTEGER,
        user_name TEXT,
        center_id INTEGER,
        center_name TEXT,
        center_place TEXT,
        slot_date DATE,
        slot_timing TEXT,
        status INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES User(id),
        FOREIGN KEY (center_id) REFERENCES Vacc_Center(id),
        FOREIGN KEY (slot_id) REFERENCES Slots(id)
    )
''')


def next_n_days(n):
    current_date = datetime.now().date()
    next_n_dates = []
    for i in range(1, n+1):
        delta = timedelta(days=i)
        future_date = current_date + delta
        formatted_date = future_date.strftime("%Y-%m-%d")
        next_n_dates.append(formatted_date)
    return next_n_dates

def curr_date():
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    return formatted_date

def OTP():
    return random.randint(100000, 999999)

def g_mail(to_email,subject,body):

    gmail_user = "shrisampleworkspace@gmail.com"
    gmail_password = "Shri36465"


    email_text = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (gmail_user, to_email, subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, email_text)
        server.close()

        print('Email sent!')
    except Exception as e:
        print(e)
        print('Something went wrong...')

def g__mail(to_email,subject,body):

    gmail_user = "shrisampleworkspace@gmail.com"
    gmail_password = "Shri36465"


    email_text = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (gmail_user, to_email, subject, body)

    try:
        # Send the email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to_email, email_text)
        server.close()

        print('Email sent!')
        return 1
    except Exception as e:
        print(e)
        print('Something went wrong...')
        return 0

# User signup logic
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    try:
        if request.method == 'POST':
            # Get the user signup form data
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']

            otp=OTP()
            print(otp)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO admin (name, email_id, password, ph_no, otp, date) VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, otp, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect('/admin/login')
    except:
        return render_template('admin_signup.html',error="Email-Id already Exists!")

    return render_template('admin_signup.html')



@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']

            otp=OTP()
            print(otp)
            

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO user (name, email_id, password, ph_no, otp, date) VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, otp, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect('/login')
    except:
        return render_template('signup.html',error="Email-Id already Exists!")

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM user WHERE email_id = ?
            '''
            cursor.execute(user_query, (email,))
            user = cursor.fetchone()
            
            if user:
                stored_password = user[3]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):

                    session['user_id'] = user[2]

                    cursor.close()
                    conn.close()
                    return redirect('/')
            

            cursor.close()
            conn.close()
            return render_template('login.html', error="Invalid Credentials!")
    except:
        render_template('login.html', error="Server Down Try Again Later.")
    

    return render_template('login.html')


@app.route("/forget_password", methods=["POST","GET"])
def forget_password():
    try:
        if request.method == "POST":
            email = request.form["email"]
            otp = OTP()
            g_mail(email,f"Recover Your Account!", f"Change the Password! \nVerify your Email by entering this OTP to change Password. \n Your OTP is {otp}.")
            return render_template("user_forget_password.html", status = 1, success="OTP sent. Check mail.")
        return render_template("user_forget_password.html", status = 0)
    except:
        return render_template('user_forget_password.html', error = "Email id not found! Please your Email.")
    


@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT name FROM Vacc_Center")
            centers = cursor.fetchall()
            cursor.execute("SELECT DISTINCT place FROM Vacc_Center")
            places = cursor.fetchall()
            cursor.execute("SELECT DISTINCT slot_timing FROM Slots")
            hours = cursor.fetchall()

            cursor.execute("SELECT DISTINCT date FROM Slots")
            dates = cursor.fetchall()

            cursor.execute("SELECT * FROM User WHERE email_id = ?",(user_id,))
            user = cursor.fetchone() 


            cursor.execute("SELECT * FROM history WHERE user_id = ?",(user[0],))
            user_history = cursor.fetchall()
            print(user_history)

            status = user[7]
            if status == 0:
                cursor.execute('''UPDATE user SET status = ? WHERE id = ?''', (1, user[0]))
            name=user[1]
            print("slot :", user)
            balance = user[6]

            if request.method == 'POST':
                center = request.form['center']
                place = request.form['place']
                hour = request.form['hour']
                date = request.form['date']


               #search functionality
                if center == "No Filter" and hour == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots")
                elif center == "No Filter" and hour == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE date = ?", (date,))
                elif center == "No Filter" and hour == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE place = ?", (place,))
                elif center == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ?", (hour,))
                elif hour == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ?", (center,))
                elif center == "No Filter" and hour == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE place = ? AND date = ?", (place, date))
                elif center == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND date = ?", (hour, date))
                elif center == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ?", (hour, place))
                elif hour == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND date = ?", (center, date))
                elif hour == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ?", (center, place))
                elif place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ?", (center, hour))
                elif center == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ? AND date = ?", (hour, place, date))
                elif hour == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ? AND date = ?", (center, place, date))
                elif place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND date = ?", (center, hour, date))
                elif date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ?", (center, hour, place))
                else:
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ? AND date = ?", (center, hour, place, date))

                rows = cursor.fetchall()
                cursor.close()
                conn.close()

                return render_template('user_dash.html', show_logout=True, centers=centers, places=places, hours = hours, dates=dates, rows=rows, name=name, user_history=user_history, balance=balance)

            cursor.close()
            conn.close()

            return render_template('user_dash.html', show_logout=True, centers=centers, places=places, hours = hours, dates=dates, name= name, balance=balance)
        else:
            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            cursor.execute("SELECT DISTINCT name FROM Vacc_Center")
            centers = cursor.fetchall()
            cursor.execute("SELECT DISTINCT place FROM Vacc_Center")
            places = cursor.fetchall()
            cursor.execute("SELECT DISTINCT slot_timing FROM Slots")
            hours = cursor.fetchall()
            cursor.execute("SELECT DISTINCT date FROM Slots")
            dates = cursor.fetchall()


            if request.method == 'POST':
                center = request.form['center']
                place = request.form['place']
                hour = request.form['hour']
                date = request.form['date']

                print("This is debugging",center,place,hour,date)

                if center == "No Filter" and hour == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots")
                elif center == "No Filter" and hour == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE date = ?", (date,))
                elif center == "No Filter" and hour == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE place = ?", (place,))
                elif center == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ?", (hour,))
                elif hour == "No Filter" and place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ?", (center,))
                elif center == "No Filter" and hour == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE place = ? AND date = ?", (place, date))
                elif center == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND date = ?", (hour, date))
                elif center == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ?", (hour, place))
                elif hour == "No Filter" and place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND date = ?", (center, date))
                elif hour == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ?", (center, place))
                elif place == "No Filter" and date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ?", (center, hour))
                elif center == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ? AND date = ?", (hour, place, date))
                elif hour == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ? AND date = ?", (center, place, date))
                elif place == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND date = ?", (center, hour, date))
                elif date == "No Filter":
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ?", (center, hour, place))
                else:
                    cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ? AND date = ?", (center, hour, place, date))

                rows = cursor.fetchall()

                cursor.close()
                conn.close()


                return render_template('home.html', show_logout=False, centers=centers, places=places, hours = hours, dates=dates, rows=rows)


            cursor.close()
            conn.close()
            

            return render_template('home.html', show_logout=False, centers=centers, places=places, hours = hours, dates=dates)
    except Exception as e:
        print(e)
        return "Ran into Some Issues. Please go back and try again."


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    try:

        if 'user_id' in session:
            user_id = session['user_id']
            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email_id = ?
            '''
            cursor.execute(user_query, (user_id,))
            user = cursor.fetchone()
            
            if user:
                # name = user[1]
                cursor.close()
                conn.close()
                
                return redirect('/admin/dashboard')
    except:
        return "Ran into Some Issues go back and Try Again."
        
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email_id = ?
            '''
            cursor.execute(user_query, (email,))
            user = cursor.fetchone()
            
            if user:
                stored_password = user[3]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password):
                    session['user_id'] = user[2]
                    cursor.close()
                    conn.close()

                    return redirect('/admin/dashboard')

            cursor.close()
            conn.close()
            return render_template("admin_login.html", error="Invalid Credntials!!")
    except:
        return "Ran into Some Issues go back and Try Again."
    

    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    try:

        if 'user_id' in session:
            user_id = session['user_id']
            

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email_id = ?
            '''
            cursor.execute(user_query, (user_id,))
            user = cursor.fetchone()
            
            if user:
                name = user[1]
                table_query = '''
                SELECT * FROM Admin
                '''
                cursor.execute(table_query)
                table_data = cursor.fetchall()

                table_query2 = '''
                SELECT * FROM Vacc_Center
                '''
                cursor.execute(table_query2)
                table_data2 = cursor.fetchall()

                center_details = '''
                SELECT * FROM Vacc_Center WHERE admin_id = ?
                '''
                cursor.execute(center_details, (int(user[0]),))
                center_details = cursor.fetchall()
                table_query = '''
                SELECT * FROM User
                '''
                cursor.execute(table_query)
                table_data3 = cursor.fetchall()

                table_query5= '''SELECT * FROM Slots'''
                cursor.execute(table_query5)
                table_data5 = cursor.fetchall()

                table_data4=[]

                for i in range(len(center_details)):
                    table_query = '''
                    SELECT * FROM slots_timing WHERE center_id = ?
                    '''
                    cursor.execute(table_query, (center_details[i][0],))
                    table_data4.append(cursor.fetchall())
                cursor.execute("SELECT DISTINCT name FROM Vacc_Center")
                centers = cursor.fetchall()
                cursor.execute("SELECT DISTINCT place FROM Vacc_Center")
                places = cursor.fetchall()
                cursor.execute("SELECT DISTINCT slot_timing FROM Slots")
                hours = cursor.fetchall()
                cursor.execute("SELECT DISTINCT date FROM Slots")
                dates = cursor.fetchall()

                if request.method == 'POST':
                    center = request.form['center']
                    place = request.form['place']
                    hour = request.form['hour']
                    date = request.form['date']

                    print("This is debugging",center,place,hour,date)

                    if center == "No Filter" and hour == "No Filter" and place == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots")
                    elif center == "No Filter" and hour == "No Filter" and place == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE date = ?", (date,))
                    elif center == "No Filter" and hour == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE place = ?", (place,))
                    elif center == "No Filter" and place == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE slot_timing = ?", (hour,))
                    elif hour == "No Filter" and place == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ?", (center,))
                    elif center == "No Filter" and hour == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE place = ? AND date = ?", (place, date))
                    elif center == "No Filter" and place == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND date = ?", (hour, date))
                    elif center == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ?", (hour, place))
                    elif hour == "No Filter" and place == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND date = ?", (center, date))
                    elif hour == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ?", (center, place))
                    elif place == "No Filter" and date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ?", (center, hour))
                    elif center == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE slot_timing = ? AND place = ? AND date = ?", (hour, place, date))
                    elif hour == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND place = ? AND date = ?", (center, place, date))
                    elif place == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND date = ?", (center, hour, date))
                    elif date == "No Filter":
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ?", (center, hour, place))
                    else:
                        cursor.execute("SELECT * FROM Slots WHERE center_name = ? AND slot_timing = ? AND place = ? AND date = ?", (center, hour, place, date))

                    table_data5 = cursor.fetchall()


                cursor.close()
                conn.close()
                
                return render_template('admin_dash.html', name=name, table_data=table_data, table_data2=table_data2, 
                                       table_data3=table_data3, table_data4=table_data4, table_data5=table_data5,
                                       centers=centers, places=places, hours = hours, dates=dates)
            else:

                status = user[7]
                if status == 0:
                    cursor.execute('''UPDATE user SET status = ? WHERE id = ?''', (1, user[0]))
                name = user[1]
                id = user[0]
                center_query = '''
                SELECT * FROM Vacc_Center WHERE admin_id = ?
                '''
                
                center_details = '''
                SELECT * FROM Vacc_Center WHERE admin_id = ?
                '''
                cursor.execute(center_details, (int(user[0]),))
                center_details = cursor.fetchall()

                table_data4=[]
                for i in range(len(center_details)):
                    table_query = '''
                    SELECT * FROM slots_timing WHERE center_id = ?
                    '''
                    cursor.execute(table_query, (center_details[i][0],))
                    table_data4.append(cursor.fetchall())

                cursor.execute(center_query, (id,))
                table_data = cursor.fetchall()

                cursor.close()
                conn.close()
                print("working fine")
                
                return render_template('vacc_center.html', name=name, table_data=table_data, table_data4=table_data4)
        else:
            return redirect('/admin/login')
        
    except Exception as e:
        print("Isuue is raising here in admin dashboard", e)
        return "Ran into Some Issues, go back and Try Again."


@app.route('/admin/add_admin', methods=['GET', 'POST'])
def add_admin():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']
            otp=OTP()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO admin ( name, email_id, password, ph_no, otp, date) VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, otp, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            g_mail(email,f"Welcome to  Vaccination Booking {name} Admin!", f"Create your Centers for booking vaccines slots! \nVerify your Email by entering this OTP once you LogIn. \n Your OTP is {otp}.")

            return  redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    try:
        if request.method == 'POST':

            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']
            otp=OTP()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO user ( name, email_id, password, ph_no, otp, date) VALUES (?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, otp, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            g_mail(email,f"Welcome to Vaccination Booking {name}!", f"Book your slot Today! \nVerify your Email by entering this OTP once you LogIn. \n Your OTP is {otp}.")

            return  redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')


@app.route('/admin/remove/<int:id>', methods=['GET', 'POST'])
def remove_admin(id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid.db')
            cursor = connection.cursor()
            
            try:
                cursor.execute("DELETE FROM Admin WHERE id = ?", (id,))
                connection.commit()
                flash('Admin successfully removed')
            except sqlite3.Error as e:
                connection.rollback()
                flash('An error occurred while removing the admin')
                print('SQLite error occurred:', e.args[0])

            connection.close()
    except:
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/remove_user/<int:id>', methods=['GET', 'POST'])
def remove_user(id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid.db')
            cursor = connection.cursor()
            
            try:
                cursor.execute("DELETE FROM user WHERE id = ?", (id,))
                connection.commit()
                flash('Admin successfully removed')
            except sqlite3.Error as e:
                connection.rollback()
                flash('An error occurred while removing the admin')
                print('SQLite error occurred:', e.args[0])

            connection.close()
    except:
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')


@app.route('/admin/add_center', methods=['GET', 'POST'])
def add_centre():

    try:
        if request.method == 'POST' and 'user_id' in session:
            
            admin_email_id = session['user_id']

            center_name = request.form['center_name']
            place = request.form['place']
            working_hour = request.form['working_hour']
            dosage = request.form['dosage']
            slots = request.form['slots']
            slot_vaccine=request.form['per_slot']
            vacc_name=request.form['vacc_name']

            conn = sqlite3.connect('covid.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            user_query = '''
            SELECT * FROM admin WHERE email_id = ?
            '''
            cursor.execute(user_query, (admin_email_id,))
            user = cursor.fetchone()
            
            
            insert_user_query = '''
            INSERT INTO Vacc_Center (name, place, working_hour, dosage, slots, slot_vaccine, vaccine_name, date, admin_id, admin_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (center_name, place, working_hour, dosage, slots, slot_vaccine, vacc_name, date(), user[0], user[1]))
            conn.commit()
            


            dates = next_n_days(math.ceil(int(dosage)/(int(slots)*int(slot_vaccine))))

            cursor.execute("SELECT dosage FROM Vacc_Center WHERE name = ? AND admin_id = ? GROUP BY centre_id", (center_name, user[0]))
            table_data2 = cursor.fetchall()

            for i in range(int(slots)):
                cursor.execute('''INSERT INTO slots_timing (center_id, center_name) VALUES (?,?)''', (table_data2[0][0],center_name,))
                conn.commit()
            
            cursor.execute("Select * FROM slots_timing where center_id = ?", (table_data2[0][0],))
            slot_timing_ids = cursor.fetchall()
            print(slot_timing_ids)

            for i in range(int(dosage)):
                insert_user_query= '''
                        INSERT INTO Slots (center_id, center_name, slot_timing_id, date, place) VALUES (?,?,?,?,?)
                        '''
                cursor.execute(insert_user_query, (table_data2[0][0],center_name,slot_timing_ids[(i//int(slot_vaccine))%int(slots)][0],dates[i//(int(slots)*int(slot_vaccine))], place))
                conn.commit()

            cursor.close()
            conn.close()

            return  redirect('/admin/dashboard')
        
    except Exception as e:
        print(e)
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')


@app.route('/admin/remove_center/<int:center_id>', methods=['GET', 'POST'])
def remove_center(center_id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid.db')
            cursor = connection.cursor()
            
            try:
                cursor.execute("DELETE FROM Vacc_center WHERE id = ?", (center_id,))
                connection.commit()
                flash('Vaccination center successfully removed')
            except sqlite3.Error as e:
                connection.rollback()
                flash('An error occurred while removing the vaccination center')
                print('SQLite error occurred:', e.args[0])

            connection.close()
    except:
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/edit_time/<int:admin_id>', methods=['GET', 'POST'])
def edit_time(admin_id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid.db')
            cursor = connection.cursor()
            slot_timing = request.form.get('slot_timing')
            if slot_timing:
            
                try:
                    cursor.execute('UPDATE slots_timing SET slot_timing = ? WHERE id = ?', (slot_timing, admin_id))
                    cursor.execute('UPDATE slots SET slot_timing = ? where slot_timing_id = ? ', ( slot_timing, admin_id))
                    connection.commit()
                    flash('Vaccination center successfully removed')
                except sqlite3.Error as e:
                    connection.rollback()
                    flash('An error occurred while removing the vaccination center')
                    print('SQLite error occurred:', e.args[0])

                connection.close()
                return jsonify(success=True)
            else:
                return jsonify(success=False, error='Invalid slot timing')

    except:
        return "Ran into Some Issues go back and Try Again."

    return redirect('/admin/dashboard')


@app.route('/book-slot', methods=['POST'])
def book_slot():
    if 'user_id' in session:            
        email_id = session['user_id']
        slot_id = request.json['center_id']
        conn = sqlite3.connect('covid.db')
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()

        user_query = '''
            SELECT * FROM user WHERE email_id = ?
            '''
        cursor.execute(user_query, (email_id,))
        user = cursor.fetchone()

        cursor.execute("BEGIN IMMEDIATE")

        try:
            query = "SELECT * FROM Slots WHERE id = ? AND status = 0"
            cursor.execute(query, (slot_id,))
            row = cursor.fetchone()

            if row is not None:
                query = "UPDATE Slots SET user_id = ?, user_name = ?, email = ?, status = 1 WHERE id = ?"
                cursor.execute(query, (user[0], user[1], email_id, slot_id))
                query = "UPDATE Vacc_Center SET dosage = dosage - 1 WHERE id = ?"
                cursor.execute(query, (row[1],))
                query = "UPDATE USER SET balance = balance - 25 where id = ?"
                cursor.execute(query, (user[0],))
                query = "INSERT INTO history (slot_id, user_id, user_name, center_id, center_name, center_place, slot_date, slot_timing, status) VALUES (?,?,?,?,?,?,?,?,?)"
                cursor.execute(query, (slot_id,user[0],user[1],row[1],row[2],row[9],row[8],row[6],1,))

                conn.commit()
                return "Slot Successfully Booked!"

            else:
                return "Slot is not available"

        except Exception as e:
            conn.rollback()
            print(e)
            return "An error occurred:"

        finally:
            conn.commit()


            conn.close()
    else:
        return redirect('/login')



@app.route('/search')
def search():
    return "Search page"

@app.route('/apply')
def apply():
    return "Apply page"


@app.route('/admin/dosage_details')
def dosage_details():
    return "Get dosage details page"


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
