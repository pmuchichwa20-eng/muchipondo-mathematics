
import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

DATABASE = "educare.db"


def create_admin():
    print("MuchiPondo Mathematics - Administrator Setup")
    print("-" * 45)

    email = input("Enter administrator email: ").strip().lower()

    if not email or "@" not in email:
        print("Error: Please enter a valid email address.")
        return

    password = getpass("Create administrator password: ")

    if len(password) < 12:
        print("Error: Use a password of at least 12 characters.")
        return

    confirm_password = getpass("Confirm administrator password: ")

    if password != confirm_password:
        print("Error: The passwords do not match.")
        return

    connection = sqlite3.connect(DATABASE)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute(
            "SELECT id FROM admins WHERE email = ?",
            (email,)
        )

        if cursor.fetchone():
            print("An administrator with this email already exists.")
            return

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO admins (email, password_hash)
            VALUES (?, ?)
        """, (email, password_hash))

        connection.commit()
        print("\nAdministrator account created successfully.")
        print("Keep your login credentials private.")

    except sqlite3.Error as error:
        connection.rollback()
        print("Database error:", error)

    finally:
        connection.close()


if __name__ == "__main__":
    create_admin()
