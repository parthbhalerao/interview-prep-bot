import sqlite3
import datetime

class User:
    def __init__(self, phone_number: str, db_path: str = 'app/data/users.db'):
        self.phone_number: str = phone_number
        self.db_path: str = db_path

        # Initialize user information
        self.user_info = None  # This will be a dictionary containing user data

        # Ensure the table exists
        self._create_users_db()
        self._add_missing_columns()

        # Load user information or create a new user
        self.user_info = self.get_user_info()
        if not self.user_info:
            self.create_user()
            self.user_info = self.get_user_info()  # Fetch the user info after creation

    def _create_users_db(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                phone_number TEXT UNIQUE NOT NULL,
                                name TEXT,
                                conversation_stage TEXT DEFAULT 'initial',
                                last_advice TEXT DEFAULT NULL,
                                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                interview_type TEXT DEFAULT NULL,
                                interview_role TEXT DEFAULT NULL,
                                last_interview_question TEXT DEFAULT NULL,
                                last_adapted_question TEXT DEFAULT NULL,
                                interview_response TEXT DEFAULT NULL,
                                last_follow_up_question TEXT DEFAULT NULL,
                                follow_up_response TEXT DEFAULT NULL
                            );''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def _add_missing_columns(self):
        conn = self._connect()
        cursor = conn.cursor()
        columns = [
            ('interview_type', 'TEXT', 'NULL'),
            ('interview_role', 'TEXT', 'NULL'),
            ('last_interview_question', 'TEXT', 'NULL'),
            ('interview_response', 'TEXT', 'NULL'),
            ('last_follow_up_question', 'TEXT', 'NULL'),
            ('follow_up_response', 'TEXT', 'NULL'),
            ('last_interaction', 'TIMESTAMP', 'CURRENT_TIMESTAMP')
        ]
        for column_name, data_type, default_value in columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {data_type} DEFAULT {default_value};")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    # Column already exists, ignore
                    pass
                else:
                    print(f"An error occurred while adding column {column_name}: {e}")
        conn.commit()
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

    def update_last_interaction(self):
        if self.user_exists():
            current_time = datetime.datetime.utcnow()
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_interaction = ? WHERE phone_number = ?",
                (current_time, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['last_interaction'] = current_time
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_interaction(self):
        self.user_info = self.get_user_info()  # Refresh user info
        if self.user_exists():
            return self.user_info.get('last_interaction')
        else:
            return None

    def get_conversation_stage(self):
        self.user_info = self.get_user_info() # Refresh user info
        if self.user_exists():
            return self.user_info.get('conversation_stage')
        else:
            return None

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

    #############################
    # Interview User Attributes #
    #############################
    def set_interview_type(self, interview_type):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET interview_type = ? WHERE phone_number = ?",
                (interview_type, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['interview_type'] = interview_type
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_interview_type(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('interview_type', '')
        else:
            return ''

    def set_interview_role(self, role):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET interview_role = ? WHERE phone_number = ?",
                (role, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['interview_role'] = role
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_interview_role(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('interview_role', '')
        else:
            return ''


    def set_last_interview_question(self, question):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_interview_question = ? WHERE phone_number = ?",
                (question, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['last_interview_question'] = question
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_interview_question(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('last_interview_question', '')
        else:
            return ''

    def set_interview_response(self, user_response):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET interview_response = ? WHERE phone_number = ?",
                (user_response, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['interview_response'] = user_response
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_interview_response(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('interview_response', '')
        else:
            return ''

    def set_last_follow_up_question(self, follow_up_question):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET last_follow_up_question = ? WHERE phone_number = ?",
                (follow_up_question, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['last_interview_question'] = follow_up_question
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_follow_up_question(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('last_follow_up_question', '')
        else:
            return ''

    def set_follow_up_response(self, user_response):
        if self.user_exists():
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET follow_up_response = ? WHERE phone_number = ?",
                (user_response, self.phone_number)
            )
            conn.commit()
            conn.close()
            self.user_info['follow_up_response'] = user_response
        else:
            print(f"User {self.phone_number} does not exist.")

    def get_last_follow_up_response(self):
        self.user_info = self.get_user_info()  # Refresh the user info
        if self.user_exists():
            return self.user_info.get('follow_up_response', '')
        else:
            return ''
