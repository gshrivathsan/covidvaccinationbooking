import sqlite3

conn = sqlite3.connect('covid_vaccine.db')
conn.execute('PRAGMA foreign_keys = ON;')
cursor = conn.cursor()

#TABLES AVAILABLE IN COVID_VACCINE.DB


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
