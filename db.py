import sqlite3

DB_NAME = 'gym.db'

def get_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT SSN FROM Person LIMIT 1")
    except sqlite3.OperationalError:
        create_tables(conn)
    return conn

def create_tables(conn):
    cursor = conn.cursor()
    
    # --- PEOPLE & CONTACT ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS Person (
        SSN INTEGER PRIMARY KEY,
        FirstName VARCHAR(100), MiddleName VARCHAR(100), LastName VARCHAR(100),
        Gender CHAR(6), DateOfBirth DATE, Address VARCHAR(255)
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Person_Phone (
        SSN INTEGER, PhoneNumber VARCHAR(15),
        PRIMARY KEY(SSN, PhoneNumber),
        FOREIGN KEY(SSN) REFERENCES Person(SSN)
    )''')
    
    # --- ROLES ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS Trainer (
        SSN INTEGER PRIMARY KEY, Branch VARCHAR(100), Salary DECIMAL(10, 2), HireDate DATE,
        FOREIGN KEY(SSN) REFERENCES Person(SSN))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Receptionist (
        SSN INTEGER PRIMARY KEY, Shift VARCHAR(50), Salary DECIMAL(10, 2), HireDate DATE,
        FOREIGN KEY(SSN) REFERENCES Person(SSN))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS GymMember (
        SSN INTEGER PRIMARY KEY, TrainerSSN INTEGER,
        FOREIGN KEY(SSN) REFERENCES Person(SSN), 
        FOREIGN KEY(TrainerSSN) REFERENCES Trainer(SSN))''')

    # --- MEMBERSHIP & INVENTORY ---
    cursor.execute('''CREATE TABLE IF NOT EXISTS Membership (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Price DECIMAL(10, 2), Type VARCHAR(50),
        StartDate DATE, EndDate DATE,
        MemberSSN INTEGER, ReceptionistSSN INTEGER,
        FOREIGN KEY(MemberSSN) REFERENCES GymMember(SSN),
        FOREIGN KEY(ReceptionistSSN) REFERENCES Receptionist(SSN))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Equipment (
        ID INTEGER PRIMARY KEY AUTOINCREMENT, Name VARCHAR(150), Type VARCHAR(100))''')

def init_db():
    conn = get_db()
    conn.close()

if __name__ == "__main__":
    init_db()