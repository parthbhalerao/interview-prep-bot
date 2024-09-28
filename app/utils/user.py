import sqlite3

class User:
    def __init__(self, phone_number: str, db_path: str = 'app/data/users.db'):
        self.phone_number: str = phone_number
        self.db_path: str = db_path

        # Initialize user information
        self.user_info = None  # This will be a dictionary containing user data

        # Ensure the table exists
        self._create_users_db()

        # Load user information or create a new user
        self.user_info = self.get_user_info()
        if not self.user_info:
            self.create_user()
            self.user_info = self.get_user_info()  # Fetch the user info after creation

    def _create_users_db(self):
        # Same as before
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                phone_number TEXT UNIQUE NOT NULL,
                                name TEXT,
                                conversation_stage TEXT DEFAULT 'initial',
                                last_advice TEXT DEFAULT NULL
                            );''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn

    def user_exists(self):
        # Use self.user_info to determine if the user exists
        return self.user_info is not None

    def create_user(self):
        conn = self._connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (phone_number, name, conversation_stage) VALUES (?, ?, ?)",
                (self.phone_number, 'User', 'initial')
            )
            conn.commit()
            print(f"User {self.phone_number} added successfully.")
        except sqlite3.IntegrityError:
            print(f"User {self.phone_number} already exists.")
        finally:
            conn.close()

    def get_user_info(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE phone_number = ?", (self.phone_number,))
        user_info = cursor.fetchone()
        conn.close()

        if user_info:
            return dict(user_info)
        else:
            return None

    def update_user_name(self, user_name):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET name = ? WHERE phone_number = ?", (user_name, self.phone_number))
            conn.commit()
            conn.close()
            print(f"User {self.phone_number}'s name updated to {user_name}.")
            # Update self.user_info
            self.user_info['name'] = user_name
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_user_name(self):
        if self.user_exists():
            return self.user_info.get('name', 'User')
        else:
            return 'User'

    def get_user_number(self) -> str:
        return self.phone_number

    def get_conversation_stage(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('conversation_stage', 'initial')
        else:
            print("Can't find conversation_stage")
            return 'initial'


    def set_conversation_stage(self, new_stage):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET conversation_stage = ? WHERE phone_number = ?",
                (new_stage, self.phone_number)
            )
            conn.commit()
            conn.close()
            # Update self.user_info
            self.user_info['conversation_stage'] = new_stage
        else:
            print(f"Can't change the conversation stage. User doesn't exist")

    def set_last_advice(self, advice):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_advice = ? WHERE phone_number = ?",
                (advice, self.phone_number)
            )
            conn.commit()
            conn.close()
            # Update self.user_info
            self.user_info['last_advice'] = advice
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_advice(self):
        if self.user_exists():
            return self.user_info.get('last_advice', None)
        else:
            return None
