from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from utils.helper import User  # Import the User class from helper.py

app = Flask(__name__)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    # Get the user's phone number and message from the incoming WhatsApp request
    user_number = request.form.get('From')
    user_msg = request.form.get('Body')

    # Extract the phone number without the 'whatsapp:' prefix
    user_number = user_number.split(':')[1]

    # Create a User instance for this phone number
    user = User(phone_number=user_number)

    # Check if the user is a first-time sender or returning user
    if user.user_exists():
        # Returning user: Fetch user info and send a custom message
        user_info = user.get_user_info()
        test = f"Welcome back {user_info[1] if user_info[1] else 'User'}! You said: {user_msg}"
    else:
        # First-time user: Insert the phone number into the database
        user.create_user()
        test = f"Thank you for joining! Your number has been registered. You said: {user_msg}"

    # Initializing Twilio's Message
    bot_resp = MessagingResponse()
    msg = bot_resp.message()
    msg.body(test)

    return str(bot_resp)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001)
