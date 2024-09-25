import sqlite3

class User:
    def __init__(self, phone_number : str, db_path : str = 'app/data/users.db'):
        self.phone_number : str = phone_number
        self.db_path : str = db_path
        self.username : str = 'User'
        self.conversation_stage : str = 'initial'

        # Call the method to ensure the table exists
        self._create_users_db()
        self.create_user()

    
    def _create_users_db(self):
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create the users table if it doesn't exist
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                phone_number TEXT UNIQUE NOT NULL,
                                name TEXT,
                                conversation_stage TEXT DEFAULT 'initial'
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

    def create_user(self):
        """
        Inserts the user into the database with their phone number and optional name.
        """
        if not self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (phone_number , name, conversation_stage) VALUES (?, ?, ?)", (self.phone_number, self.username, self.conversation_stage))
                conn.commit()
                print(f"User {self.phone_number} added successfully.")
            except sqlite3.IntegrityError:
                print(f"User {self.phone_number} already exists.")
            finally:
                conn.close()
        else:
            print(f"User {self.phone_number} already exists in the system.")
    
    def update_conversation_stage(self, stage):
        """Update the user's conversation stage in the database."""
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET conversation_stage = ? WHERE phone_number = ?", (stage, self.phone_number))
        conn.commit()
        conn.close()

    def get_user_name(self):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM users WHERE phone_number = ?", (self.phone_number))            

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
        """Fetch the user's information including the conversation state."""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute("SELECT phone_number, name, conversation_stage FROM users WHERE phone_number = ?", (self.phone_number,))
        user_info = cursor.fetchone()  # Fetch the user information

        conn.close()

        # Return the fetched user info or None if no data was found
        if user_info:
            self.phone_number, self.name, self.conversation_stage = user_info  # Update the instance attributes
            return user_info
        return None

    def get_conversation_stage(self):
        user_info = self.get_user_info()
        
        if user_info and len(user_info) >= 3:
            conversation_stage = user_info[2]  # The conversation_stage is the third element
            return conversation_stage
        else:
            print("Can't find conversation_stage")
    
    def set_conversation_stage(self, new_stage):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()

            # Update the conversation stage for the user
            cursor.execute("UPDATE users SET conversation_stage = ? WHERE phone_number = ?", 
                       (new_stage, self.phone_number))
            conn.commit()
            conn.close()

            # Update the local instance's stage
            self.conversation_stage = new_stage
        else:
            print(f"Can't change the conversation stage. User doesn't exist")







