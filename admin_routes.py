from flask import Blueprint
from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from helper import next_n_days, curr_date
import sqlite3
import bcrypt
import math

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/signup', methods=['GET', 'POST'])
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


@admin_bp.route('/admin/login', methods=['GET', 'POST'])
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


@admin_bp.route('/admin/dashboard', methods=['GET', 'POST'])
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

                table_query5 = '''SELECT * FROM Slots'''
                cursor.execute(table_query5)
                table_data5 = cursor.fetchall()

                table_data4 = []

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

                    print("This is debugging", center, place, hour, date)
                    query = "SELECT * FROM Slots WHERE"
                    params = []

                    if center != "No Filter":
                        query += " lower(center) = lower(?) AND"
                        params.append(center)

                    if place != "No Filter":
                        query += " lower(place) = lower(?) AND"
                        params.append(place)

                    if hour != "No Filter":
                        query += " lower(slot_timing) = lower(?) AND"
                        params.append(hour)

                    if date != "No Filter":
                        query += " lower(date) = lower(?) AND"
                        params.append(date)

                    query = query.rstrip("AND")
                    cursor.execute(query, params)

                    table_data5 = cursor.fetchall()

                cursor.close()
                conn.close()

                return render_template('admin_dash.html', name=name, table_data=table_data, table_data2=table_data2,
                                       table_data3=table_data3, table_data4=table_data4, table_data5=table_data5,
                                       dosage_data=dosage_data,
                                       centers=centers, places=places, hours=hours, dates=dates)
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

                table_data4 = []
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


@admin_bp.route('/admin/add_admin', methods=['GET', 'POST'])
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
            return redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')


@admin_bp.route('/admin/add_user', methods=['GET', 'POST'])
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

            return redirect('/admin/dashboard')
    except Exception as e:
        print(e)
        return "An error occurred. Try Again."

    return redirect('/admin/dashboard')


@admin_bp.route('/admin/remove/<int:id>', methods=['GET', 'POST'])
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


@admin_bp.route('/admin/remove_user/<int:id>', methods=['GET', 'POST'])
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


@admin_bp.route('/admin/add_center', methods=['GET', 'POST'])
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
                center_name, place, working_hour, dosage, slots, slot_vaccine, vacc_name, curr_date(), user[0],
                user[1]))
            conn.commit()

            dates = next_n_days(math.ceil(int(dosage) / (int(slots) * int(slot_vaccine))))

            cursor.execute(
                "SELECT c.id AS center_id, c.name AS center_name, SUM(c.dosage) AS total_dosage FROM Vacc_Center c GROUP BY  c.name")
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


@admin_bp.route('/admin/dosage_details')
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


@admin_bp.route('/admin/remove_center/<int:center_id>', methods=['GET', 'POST'])
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


@admin_bp.route('/admin/remove_time/<int:admin_id>', methods=['POST'])
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


@admin_bp.route('/admin/edit_time/<int:admin_id>', methods=['GET', 'POST'])
def edit_time(admin_id):
    try:
        if request.method == 'POST':
            connection = sqlite3.connect('covid_vaccine.db')
            cursor = connection.cursor()
            slot_timing = request.form.get('slot_timing')
            if slot_timing:

                try:
                    cursor.execute('UPDATE slots_timing SET slot_timing = ? WHERE id = ?', (slot_timing, admin_id))
                    cursor.execute('UPDATE slots SET slot_timing = ? where slot_timing_id = ? ',
                                   (slot_timing, admin_id))
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


