from flask import Flask, request
from utils.user import User
from model.conversation import Conversation

app = Flask(__name__)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        # Extract the user's phone number from the request
        user_number = extract_number()

        # Create a User instance with the phone number
        user = User(user_number)

        # If the user doesn't exist in the database, create a new user
        if not user.user_exists():
            user.create_user()
            print('New User created')

        # Create a Conversation instance, passing in the Bot instance for messaging
        conv = Conversation(user)

        # Handle the conversation logic
        conv.handle_conversation()
        print('Handling conversation')

        return "OK", 200

    except Exception as e:
        print(f"Error occurred: {e}")
        return str(e), 500


def extract_number():
    """Extracts the user's phone number from the incoming request."""
    user_number = request.form.get('From')
    user_number = user_number.split(':')[1]  # Remove the "whatsapp:" prefix
    return user_number

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001)
