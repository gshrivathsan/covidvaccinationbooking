from flask import Blueprint
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from helper import next_n_days, curr_date
from twilio.rest import Client
import random
import sqlite3
import bcrypt


user_bp = Blueprint('user', __name__)
account_sid = 'AC9e7afa8cac2bf723d775a4490bed7f21'
auth_token = '188d56141fcabcc0b11959ca2ab8fa53'
twilio_phone_number = '+15417222908'
otp_store = {}


def send_otp(phone_number):
    otp = str(random.randint(1000, 9999))
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_=twilio_phone_number,
        to=phone_number
    )
    return otp
def validate_otp(phone_number, otp):
    if phone_number in otp_store and otp_store[phone_number] == otp:
        return True
    return False

@user_bp.route('/otp_generate', methods=['GET', 'POST'])
def send_otp_route():
    if request.method == 'POST':
        phone_number = request.form['phone_number']
        otp = send_otp(phone_number)
        otp_store[phone_number] = otp
        return render_template('validate_otp.html', phone_number=phone_number)
    return render_template('send_otp.html')


@user_bp.route('/validate-otp', methods=['POST'])
def validate_otp_route():
    phone_number = request.form['phone_number']
    otp = request.form['otp']
    if validate_otp(phone_number, otp):
        return redirect('/login')
    else:
        return "Invalid OTP"




@user_bp.route('/signup', methods=['GET', 'POST'])
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

            return redirect('/otp_generate')

        except:
            return render_template('signup.html', error="Email-Id already Exists!")

    return render_template('signup.html')


@user_bp.route('/login', methods=['GET', 'POST'])
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


@user_bp.route('/book-slot', methods=['GET','POST'])
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



@user_bp.route('/about')
def about():
    if 'user_id' in session:
        return render_template('about.html')
    else:
        return redirect('/login')

@user_bp.route('/protect')
def protect():
    if 'user_id' in session:
        return render_template('protect.html')
    else:
        return redirect('/login')

