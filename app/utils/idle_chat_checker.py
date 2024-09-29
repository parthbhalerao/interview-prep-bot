import sqlite3
import datetime
from model.bot import Bot
from utils.user import User

def check_idle_conversations():
    conn = sqlite3.connect('app/data/users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    threshold_minutes = 15  # Define your inactivity threshold
    threshold_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=threshold_minutes)

    cursor.execute(
        "SELECT phone_number, conversation_stage FROM users WHERE last_interaction < ? AND conversation_stage NOT IN ('initial', 'onboarded')",
        (threshold_time.strftime('%Y-%m-%d %H:%M:%S.%f'),)
    )
    idle_users = cursor.fetchall()

    for user_data in idle_users:
        phone_number = user_data['phone_number']
        conversation_stage = user_data['conversation_stage']
        user = User(phone_number)
        to_number = user.get_user_number()
        # Send a thank you message
        bot = Bot()
        bot.say(to_number, "Thank you for chatting with us! Seems like we have disconnected. If you need anything else, just send a message.")
        # Reset conversation stage
        user.set_conversation_stage('onboarded')

    conn.close()
