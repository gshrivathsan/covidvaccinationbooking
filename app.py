from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify,Blueprint
from covid_vaccine_db import conn,cursor
import sqlite3
from user_routes import user_bp
from admin_routes import admin_bp

import datetime
import math

app = Flask(__name__)
app.secret_key ='81117add8ab027690bd40297'

app.register_blueprint(user_bp) # User routes
app.register_blueprint(admin_bp) # Admin routes


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

            cursor.execute("SELECT * FROM user WHERE email = ?", (user_id,))
            user = cursor.fetchone()

            cursor.execute("SELECT * FROM history WHERE user_id = ?", (user[0],))
            user_history = cursor.fetchall()
            print(user_history)

            status = user[6]
            if status == 0:
                cursor.execute('''UPDATE user SET status = ? WHERE id = ?''', (1, user[0]))
            name = user[1]
            print("slot :", user)
            balance = user[5]

            if request.method == 'POST':
                center = request.form['center']
                place = request.form['place']
                hour = request.form['hour']
                date = request.form['date']

                query = "SELECT * FROM Slots WHERE 1=1"
                params = []

                if center != "No Filter":
                    query += " AND lower(center_name) = lower(?)"
                    params.append(center)

                if place != "No Filter":
                    query += " AND lower(place) = lower(?)"
                    params.append(place)

                if hour != "No Filter":
                    query += " AND lower(slot_timing) = lower(?)"
                    params.append(hour)

                if date != "No Filter":
                    query += " AND lower(date) = lower(?)"
                    params.append(date)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                cursor.close()
                conn.close()

                return render_template('user_dash.html', show_logout=True, centers=centers, places=places, hours=hours,
                                       dates=dates, rows=rows, name=name, user_history=user_history, balance=balance)

            cursor.close()
            conn.close()

            return render_template('user_dash.html', show_logout=True, centers=centers, places=places, hours=hours,
                                   dates=dates, name=name, balance=balance)
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

                print("This is debugging", center, place, hour, date)

                query = "SELECT * FROM Slots WHERE 1=1"
                params = []

                if center != "No Filter":
                    query += " AND lower(center_name) = lower(?)"
                    params.append(center)

                if place != "No Filter":
                    query += " AND lower(place) = lower(?)"
                    params.append(place)

                if hour != "No Filter":
                    query += " AND lower(slot_timing) = lower(?)"
                    params.append(hour)

                if date != "No Filter":
                    query += " AND lower(date) = lower(?)"
                    params.append(date)

                cursor.execute(query, params)
                rows = cursor.fetchall()

                cursor.close()
                conn.close()

                return render_template('home.html', show_logout=False, centers=centers, places=places, hours=hours,
                                       dates=dates, rows=rows)

            cursor.close()
            conn.close()

            return render_template('home.html', show_logout=False, centers=centers, places=places, hours=hours,
                                   dates=dates)
    except Exception as e:
        print(e)
        return "An error occurred. Try Again."


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
