from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import sqlite3
import bcrypt
import twilio
import random
from twilio.rest import Client
from datetime import date, datetime, timedelta
import math

app = Flask(__name__)
app.secret_key ='81117add8ab027690bd40297'


conn = sqlite3.connect('covid_vaccine.db')
conn.execute('PRAGMA foreign_keys = ON;')
cursor = conn.cursor()
otp_dict = {}

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE, 
        pass TEXT,
        mobile INTEGER,
        balance INTEGER DEFAULT 50,
        status INTEGER DEFAULT 0,
        date DATE,
        age INT 
    )
''')

cursor.execute('''
 CREATE TABLE IF NOT EXISTS admin (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        pass TEXT,
        mobile INTEGER,
        status INTEGER DEFAULT 0,
        date DATE
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vacc_Center (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT ,
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
        FOREIGN KEY (admin_id) REFERENCES admin(id) ON DELETE CASCADE
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
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
        FOREIGN KEY (slot_timing_id) REFERENCES slots_timing(id) ON DELETE CASCADE
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
        FOREIGN KEY (user_id) REFERENCES user(id),
        FOREIGN KEY (center_id) REFERENCES Vacc_Center(id),
        FOREIGN KEY (slot_id) REFERENCES Slots(id)
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

#helper function


def otp_generation():
    return random.randint(1000, 9999)


def send_otp(phone_number,otp):

    account_sid = 'AC9e7afa8cac2bf723d775a4490bed7f21'
    auth_token = 'c2068e5f30a5562de0aa8d37588e7124'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body='Hi Im Shri. Your Secure Device OTP for Covid Vaccination is - ' + str(otp),
        from_='+15417222908',
        to='+91' + str(phone_number)
    )


def curr_date():
    current_date = datetime.now().date()
    formatted_date = current_date.strftime("%Y-%m-%d")
    return formatted_date

def next_n_days(n):
    current = datetime.now().date()
    next_n_dates = []
    for i in range(1, n+1):
        x = timedelta(days=i)
        future_date = current + x
        formatted = future_date.strftime("%Y-%m-%d")
        next_n_dates.append(formatted)
    return next_n_dates



# @app.route('/send_otp', methods=['POST'])
# def send_otp_route():
#     if request.method == 'POST':
#         phone_number = request.json.get('phone_number')
#
#         if phone_number:
#             # Send OTP
#             generated_otp = send_otp(phone_number)
#             return {'success': True, 'otp': generated_otp}
#         else:
#             return {'success': False, 'error': 'Phone number is missing.'}

@app.route('/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            age = request.form['age']
            password = request.form['password']
            ph_no = request.form['ph_no']

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            insert_user_query = '''
                                    INSERT INTO user (name, email, pass, mobile, date, age) VALUES (?, ?, ?, ?, ?, ?)
                                '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, curr_date(), age))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect('/login')

        except:
            return render_template('signup.html', error="Email-Id already Exists!")

    return render_template('signup.html')


# @app.route('/otp-verification')
# def otp_verification():
#     if request.method == 'POST' and 'user_id' in session:
#         generated_otp = otp_generation()
#         ph_no = request.args.get('ph_no')
#         send_otp(ph_no,generated_otp)
#         otp = request.form['otp']
#
#         if otp == generated_otp:
#             return redirect('/')
#         else:
#             return render_template('otp_verification.html',error="Enter the correct OTP")
#     return render_template('otp_verification.html')



@app.route('/login', methods=['GET', 'POST'])
def user_login():
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM user WHERE email = ?
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



@app.route('/', methods=['GET', 'POST'])
def home():
    try:
        if 'user_id' in session:
            user_id = session['user_id']
            conn = sqlite3.connect('covid_vaccine.db')
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

            cursor.execute("SELECT * FROM user WHERE email = ?",(user_id,))
            user = cursor.fetchone() 


            cursor.execute("SELECT * FROM history WHERE user_id = ?",(user[0],))
            user_history = cursor.fetchall()
            print(user_history)

            status = user[6]
            if status == 0:
                cursor.execute('''UPDATE user SET status = ? WHERE id = ?''', (1, user[0]))
            name=user[1]
            print("slot :", user)
            balance = user[5]

            if request.method == 'POST':
                center = request.form['center']
                place = request.form['place']
                hour = request.form['hour']
                date = request.form['date']


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
            conn = sqlite3.connect('covid_vaccine.db')
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
        return "An error occurred. Try Again."


# Admin routes
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            insert_user_query = '''
            INSERT INTO admin (name, email, pass, mobile, date) VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            return redirect('/admin/login')
    except:
        return render_template('admin_signup.html', error="Email-Id already Exists!")

    return render_template('admin_signup.html')



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    try:

        if 'user_id' in session:
            user_id = session['user_id']
            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email = ?
            '''
            cursor.execute(user_query, (user_id,))
            user = cursor.fetchone()
            
            if user:
                cursor.close()
                conn.close()
                
                return redirect('/admin/dashboard')
    except:
        return "An error occurred. Try Again."
        
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email = ?
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
        return "An error occurred. Try Again."
    

    return render_template('admin_login.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    try:

        if 'user_id' in session:
            user_id = session['user_id']
            

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            user_query = '''
            SELECT * FROM admin WHERE email = ?
            '''
            cursor.execute(user_query, (user_id,))
            user = cursor.fetchone()
            
            if user:
                name = user[1]
                table_query = '''
                SELECT * FROM admin
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
                SELECT * FROM user
                '''
                cursor.execute(table_query)
                table_data3 = cursor.fetchall()

                dosage_query = '''
                       SELECT name, SUM(dosage) AS total_dosage FROM Vacc_Center GROUP BY name
                       '''
                cursor.execute(dosage_query)
                dosage_data = cursor.fetchall()

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
                                       table_data3=table_data3, table_data4=table_data4, table_data5=table_data5,dosage_data=dosage_data,
                                       centers=centers, places=places, hours = hours, dates=dates)
            else:

                status = user[6]
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
                
                return render_template('vacci_details.html', name=name, table_data=table_data, table_data4=table_data4)
        else:
            return redirect('/admin/login')
        
    except Exception as e:
        return "An error occurred. Try Again."


@app.route('/admin/add_admin', methods=['GET', 'POST'])
def add_admin():
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO admin ( name, email, pass, mobile, date) VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()
            return  redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    try:
        if request.method == 'POST':

            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            ph_no = request.form['ph_no']
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            

            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()
            
            insert_user_query = '''
            INSERT INTO user ( name, email, pass, mobile, date) VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (name, email, hashed_password, ph_no, curr_date()))
            conn.commit()

            cursor.close()
            conn.close()

            return  redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')


@app.route('/admin/remove/<int:id>', methods=['GET', 'POST'])
def remove_admin(id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid_vaccine.db')
            cursor = connection.cursor()
            
            try:
                cursor.execute("DELETE FROM admin WHERE id = ?", (id,))
                connection.commit()
                flash('Removed Admin successfully')
            except sqlite3.Error as e:
                connection.rollback()
                flash('An error occurred while removing the admin')
                print('SQLite error occurred:', e.args[0])

            connection.close()
    except:
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/remove_user/<int:id>', methods=['GET', 'POST'])
def remove_user(id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid_vaccine.db')
            cursor = connection.cursor()
            
            try:
                cursor.execute("DELETE FROM user WHERE id = ?", (id,))
                connection.commit()
                flash('Removed User Successfully')
            except sqlite3.Error as e:
                connection.rollback()
                flash('An error occurred while removing the admin')
                print('SQLite error occurred:', e.args[0])

            connection.close()
    except:
        return "An error occurred. Try Again."

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
            slot_vaccine = request.form['per_slot']
            vacc_name = request.form['vacc_name']


            conn = sqlite3.connect('covid_vaccine.db')
            conn.execute('PRAGMA foreign_keys = ON;')
            cursor = conn.cursor()

            user_query = '''
            SELECT * FROM admin WHERE email = ?
            '''
            cursor.execute(user_query, (admin_email_id,))
            user = cursor.fetchone()

            insert_user_query = '''
            INSERT INTO Vacc_Center (name, place, working_hour, dosage, slots, slot_vaccine, vaccine_name, date, admin_id, admin_name) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            cursor.execute(insert_user_query, (
            center_name, place, working_hour, dosage, slots, slot_vaccine, vacc_name, curr_date(), user[0], user[1]))
            conn.commit()


            dates = next_n_days(math.ceil(int(dosage) / (int(slots) * int(slot_vaccine))))

            cursor.execute("SELECT c.id AS center_id, c.name AS center_name, SUM(c.dosage) AS total_dosage FROM Vacc_Center c GROUP BY  c.name")
            table_data2 = cursor.fetchall()

            for i in range(int(slots)):
                cursor.execute('''INSERT INTO slots_timing (center_id, center_name) VALUES (?,?)''',
                               (table_data2[0][0], center_name,))
                conn.commit()

            cursor.execute("Select * FROM slots_timing where center_id = ?", (table_data2[0][0],))
            slot_timing_ids = cursor.fetchall()
            print(slot_timing_ids)

            for i in range(int(dosage)):
                insert_user_query = '''
                        INSERT INTO Slots (center_id, center_name, slot_timing_id, date, place) VALUES (?,?,?,?,?)
                        '''
                cursor.execute(insert_user_query, (
                table_data2[0][0], center_name, slot_timing_ids[(i // int(slot_vaccine)) % int(slots)][0],
                dates[i // (int(slots) * int(slot_vaccine))], place))
                conn.commit()


            cursor.close()
            conn.close()


            return redirect('/admin/add_center')

    except Exception as e:
        print(e)
        return "Go back and Try Again."


    return redirect('/admin/dashboard')


@app.route('/admin/dosage_details')
def dosage_details():
    if 'user_id' in session:
        try:
            conn = sqlite3.connect('covid_vaccine.db')
            cursor = conn.cursor()

            dosage_query = '''
            SELECT name, SUM(dosage) AS total_dosage FROM Vacc_Center GROUP BY name
            '''
            cursor.execute(dosage_query)
            dosage_data = cursor.fetchall()

            cursor.close()
            conn.close()

            return dosage_data
        except Exception as e:
            print(e)
            return "An error occurred."
        return "Success"
    else:
        return redirect('/admin/login')



@app.route('/admin/remove_center/<int:center_id>', methods=['GET', 'POST'])
def remove_center(center_id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid_vaccine.db')
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
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')

@app.route('/admin/remove_time/<int:admin_id>', methods=['POST'])
def remove_time(admin_id):
    try:
        connection = sqlite3.connect('covid_vaccine.db')
        cursor = connection.cursor()
        try:
            cursor.execute('DELETE FROM slots_timing WHERE id = ?', (admin_id,))
            cursor.execute('UPDATE slots SET slot_timing_id = NULL WHERE slot_timing_id = ?', (admin_id,))
            connection.commit()
            flash('Slot timing successfully removed')
        except sqlite3.Error as e:
            connection.rollback()
            flash('An error occurred while removing the slot timing')
            print('SQLite error occurred:', e.args[0])

        connection.close()
        return jsonify(success=True)
    except:
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')


@app.route('/admin/edit_time/<int:admin_id>', methods=['GET', 'POST'])
def edit_time(admin_id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid_vaccine.db')
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
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')


@app.route('/book-slot', methods=['GET','POST'])
def book_slot():
    if 'user_id' in session:
        email_id = session['user_id']
        slot_id = request.json['center_id']
        conn = sqlite3.connect('covid_vaccine.db')
        conn.execute('PRAGMA foreign_keys = ON;')
        cursor = conn.cursor()

        user_query = '''
            SELECT * FROM user WHERE email = ?
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



@app.route('/about')
def about():
    if 'user_id' in session:
        return render_template('about.html')
    else:
        return redirect('/login')

@app.route('/protect')
def protect():
    if 'user_id' in session:
        return render_template('protect.html')
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
