import sqlite3

class User:
    def __init__(self, phone_number : str, db_path : str = './app/data/users.db'):
        self.phone_number : str = phone_number
        self.db_path : str = db_path
        self.name : str = None
    
    def _create_users_db(self):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the users table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                phone_number TEXT UNIQUE NOT NULL,
                                name TEXT
                            );''')

            # Commit changes
            conn.commit()

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            # Ensure the connection is closed
            conn.close()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        return conn

    def user_exists(self):
        # Connecting to the SQLite database
        conn = self._connect()
        cursor = conn.cursor()


        # Checking if the number exists
        cursor.execute("SELECT phone_number FROM users WHERE phone_number = ?", (self.phone_number,))

        # Fetch the result and close connection
        result = cursor.fetchone()
        conn.close()

        # Return True if number exists, else False
        return result is not None

    def create_user(self, user_name=None):
        """
        Inserts the user into the database with their phone number and optional name.
        """
        if not self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (phone_number, name) VALUES (?, ?)", (self.phone_number, user_name))
                conn.commit()
                print(f"User {self.phone_number} added successfully.")
            except sqlite3.IntegrityError:
                print(f"User {self.phone_number} already exists.")
            finally:
                conn.close()
        else:
            print(f"User {self.phone_number} already exists in the system.")

    def update_user_name(self, user_name):
        """
        Updates the user's name in the database.
        """
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = ? WHERE phone_number = ?", (user_name, self.phone_number))
            conn.commit()
            conn.close()
            print(f"User {self.phone_number}'s name updated to {user_name}.")
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_user_info(self):
        """
        Fetches user information from the database.
        """
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT phone_number, name FROM users WHERE phone_number = ?", (self.phone_number,))
        user_info = cursor.fetchone()
        conn.close()
        return user_info




