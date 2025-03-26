import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Function to create a database for train bookings
def create_database():
    conn = sqlite3.connect('train_ticket_booking.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS trains
                 (id INTEGER PRIMARY KEY, name TEXT, route TEXT, available_seats INTEGER, price REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY, train_id INTEGER, customer_name TEXT, customer_email TEXT, tickets INTEGER)''')
    
    conn.commit()
    conn.close()

# Function to add train data into the database
def add_trains():
    conn = sqlite3.connect('train_ticket_booking.db')
    c = conn.cursor()
    
    trains = [
        ("Express A", "Station1 to Station2", 50, 100.0),
        ("Express B", "Station2 to Station3", 40, 120.0),
        ("Express C", "Station1 to Station3", 30, 110.0)
    ]
    
    c.executemany('INSERT INTO trains (name, route, available_seats, price) VALUES (?, ?, ?, ?)', trains)
    
    conn.commit()
    conn.close()

# Function to view available trains
def view_trains():
    conn = sqlite3.connect('train_ticket_booking.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM trains')
    trains = c.fetchall()
    
    print("Available Trains:")
    for train in trains:
        print(f"ID: {train[0]}, Name: {train[1]}, Route: {train[2]}, Available Seats: {train[3]}, Price: ${train[4]}")
    
    conn.close()

# Function to book a ticket
def book_ticket(customer_name, customer_email, train_id, tickets):
    conn = sqlite3.connect('train_ticket_booking.db')
    c = conn.cursor()
    
    # Check if enough seats are available
    c.execute('SELECT available_seats, price FROM trains WHERE id = ?', (train_id,))
    train = c.fetchone()
    
    if train is None:
        print("Train not found.")
        return
    
    available_seats, price = train
    if tickets > available_seats:
        print("Not enough seats available.")
        return
    
    # Insert booking into the database
    c.execute('INSERT INTO bookings (train_id, customer_name, customer_email, tickets) VALUES (?, ?, ?, ?)',
              (train_id, customer_name, customer_email, tickets))
    
    # Update available seats
    new_available_seats = available_seats - tickets
    c.execute('UPDATE trains SET available_seats = ? WHERE id = ?', (new_available_seats, train_id))
    
    conn.commit()
    conn.close()
    
    # Send booking confirmation email
    send_confirmation_email(customer_email, customer_name, train[1], tickets, price, new_available_seats)

# Function to send booking confirmation email
def send_confirmation_email(to_email, customer_name, train_name, tickets, price, available_seats):
    from_email = "your_email@gmail.com"  # Replace with your email
    password = "your_password"  # Replace with your email password

    subject = "Train Ticket Booking Confirmation"
    body = f"Hello {customer_name},\n\nYour booking for {tickets} tickets on {train_name} has been confirmed.\n" \
           f"Total Price: ${tickets * price}\n" \
           f"Remaining Seats on {train_name}: {available_seats}\n\nThank you for booking with us!"
    
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Booking confirmation email sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Main function to run the booking system
def main():
    create_database()
    add_trains()  # Add train details to the database
    while True:
        print("\n1. View Trains\n2. Book a Ticket\n3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == "1":
            view_trains()
        elif choice == "2":
            customer_name = input("Enter your name: ")
            customer_email = input("Enter your email: ")
            train_id = int(input("Enter the train ID you want to book: "))
            tickets = int(input("Enter the number of tickets: "))
            book_ticket(customer_name, customer_email, train_id, tickets)
        elif choice == "3":
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()