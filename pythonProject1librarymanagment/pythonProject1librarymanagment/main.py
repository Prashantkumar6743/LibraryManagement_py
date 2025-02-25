import mysql.connector
import hashlib
import time
import datetime
from prettytable import PrettyTable

# Database Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library"
)
mycursor = mydb.cursor()

# Create Database & Tables
mycursor.execute("CREATE DATABASE IF NOT EXISTS library")
mycursor.execute("USE library")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS available_books (
        id INT PRIMARY KEY,
        name VARCHAR(25),
        subject VARCHAR(25),
        quantity INT
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS issued (
        id INT,
        name VARCHAR(25),
        subject VARCHAR(25),
        s_name VARCHAR(25),
        s_class VARCHAR(25),
        FOREIGN KEY (id) REFERENCES available_books(id) ON DELETE CASCADE
    )
""")
mycursor.execute("""
    CREATE TABLE IF NOT EXISTS login (
        user VARCHAR(25),
        password VARCHAR(64)
    )
""")
mydb.commit()

# Default Admin User
mycursor.execute("SELECT * FROM login")
if mycursor.fetchone() is None:
    default_password = hashlib.sha256("pass".encode()).hexdigest()
    mycursor.execute("INSERT INTO login (user, password) VALUES (%s, %s)", ("admin", default_password))
    mydb.commit()

# Utility: Show Loading Effect
def loading(text="Processing"):
    for _ in range(3):
        print(f"{text}...", end="\r")
        time.sleep(0.5)

# Utility: Show Table Output
def display_table(data, headers):
    table = PrettyTable()
    table.field_names = headers
    for row in data:
        table.add_row(row)
    print(table)

# Function: Add a Book
def addbook():
    print("\nAdd a New Book")
    idd = int(input("Enter Book ID: "))
    name = input("Enter Book Name: ")
    subject = input("Enter Subject: ")
    quan = int(input("Enter Quantity: "))

    mycursor.execute("INSERT INTO available_books (id, name, subject, quantity) VALUES (%s, %s, %s, %s)",
                     (idd, name, subject, quan))
    mydb.commit()
    
    loading("Adding Book")
    print("Book Added Successfully!")
    main()

# Function: Issue a Book
def issued():
    print("\nIssue a Book")
    idd = int(input("Enter Book ID: "))
    
    mycursor.execute("SELECT * FROM available_books WHERE id = %s", (idd,))
    book = mycursor.fetchone()
    
    if book and book[3] > 0:
        name, subject, quan = book[1], book[2], book[3]
        s_name = input("Enter Student Name: ")
        s_class = input("Enter Student Class: ")
        issue_date = datetime.date.today()

        mycursor.execute("INSERT INTO issued (id, name, subject, s_name, s_class, date_issued) VALUES (%s, %s, %s, %s, %s, %s)",
                         (idd, name, subject, s_name, s_class, issue_date))
        mycursor.execute("UPDATE available_books SET quantity = quantity - 1 WHERE id = %s", (idd,))
        mydb.commit()

        loading("Issuing Book")
        print(f"Book Issued to {s_name} (Class: {s_class}) on {issue_date}")
    else:
        print("Book Not Available!")
    
    main()

# Function: Return a Book
def submit():
    print("\nReturn a Book")
    idd = int(input("Enter Book ID: "))
    s_name = input("Enter Student Name: ")
    s_class = input("Enter Student Class: ")

    mycursor.execute("SELECT * FROM issued WHERE id = %s AND s_name = %s AND s_class = %s", (idd, s_name, s_class))
    issued_book = mycursor.fetchone()

    if issued_book:
        mycursor.execute("DELETE FROM issued WHERE id = %s AND s_name = %s AND s_class = %s", (idd, s_name, s_class))
        mycursor.execute("UPDATE available_books SET quantity = quantity + 1 WHERE id = %s", (idd,))
        mydb.commit()

        loading("Processing Return")
        print("Book Returned Successfully!")
    else:
        print("No Record Found!")

    main()

# Function: View Issued Books
def qoc():
    print("\nIssued Books List")
    mycursor.execute("SELECT * FROM issued")
    data = mycursor.fetchall()

    if data:
        display_table(data, ["ID", "Name", "Subject", "Student", "Class", "Date Issued"])
    else:
        print("No Books Issued Yet!")

    main()

# Function: Remove a Book
def remove():
    print("\nRemove a Book")
    idd = int(input("Enter Book ID to Remove: "))
    
    mycursor.execute("SELECT * FROM available_books WHERE id = %s", (idd,))
    if mycursor.fetchone():
        mycursor.execute("DELETE FROM available_books WHERE id = %s", (idd,))
        mydb.commit()

        loading("Removing Book")
        print("Book Removed Successfully!")
    else:
        print("Book Not Found!")
    
    main()

# Function: Display Available Books
def display():
    print("\nAvailable Books List")
    mycursor.execute("SELECT * FROM available_books")
    data = mycursor.fetchall()

    if data:
        display_table(data, ["ID", "Name", "Subject", "Quantity"])
    else:
        print("No Books Available!")

    main()
    
def search_books():
    print("\n🔍 Search for a Book by Name")
    book_name = input("Enter Book Name: ")
    
    query = "SELECT * FROM available_books WHERE name LIKE %s"
    values = (f"%{book_name}%",)
    
    mydb = mysql.connector.connect(host="localhost", user="root", password="", database="library")
    mycursor = mydb.cursor()
    mycursor.execute(query, values)
    results = mycursor.fetchall()
    
    if results:
        print("\nID | Name | Subject | Quantity")
        print("-" * 40)
        for row in results:
            print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
    else:
        print("\nNo matching books found!")
    
    mycursor.close()
    mydb.close()
    main()

# Main Menu
def main():
    print("\n---------------LIBRARY MANAGEMENT SYSTEM---------------")
    print("Select Tasks")
    print("1. Add New Book\n2. Remove a Book\n3. Issue a Book\n4. Return a Book\n5. View Available Books\n6. View Issued Books\n7. Search for Book\n8. Logout")
    
    choice = input("Enter Task Number: ")
    
    if choice == '1':
        addbook()
    elif choice == '2':
        remove()
    elif choice == '3':
        issued()
    elif choice == '4':
        submit()
    elif choice == '5':
        display()
    elif choice == '6':
        qoc()
    elif choice == '7':
        search_books()
    elif choice == '8':
        exit()
    else:
        print("Invalid Choice! Try Again.")
        main()

# Login System
while True:
    print("----------------WELCOME TO THE LIBRARY MANAGEMENT SYSTEM-----------------------")
    print("\n1. Login\n2. Exit")
    ch = input("Enter Your Choice: ")
    
    if ch == '1':
        password = input("Enter Password: ")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        mycursor.execute("SELECT * FROM login WHERE user = 'admin' AND password = %s", (hashed_password,))
        if mycursor.fetchone():
            print("Login Successful!")
            main()
        else:
            print("Incorrect Password!")
    elif ch == '2':
        exit()
    else:
        print("Invalid Choice! Try Again.")
