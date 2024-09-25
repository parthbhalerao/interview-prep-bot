from flask import Flask, request
from utils.helper import User
from model.messaging import Conversation
import json
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

def load_messages_from_json():
    """Load messages from a JSON file."""
    with open('./app/data/messages.json') as f:
        return json.load(f)

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    try:
        conv = Conversation()
        print("Conversation Created!")
        user_number = conv.extract_number()
        print(f'{user_number} sent a message')
        user = User(user_number)
        print(f'{user.phone_number} added to database.')

        if user.user_exists():
            replies = conv.handle_conversation(user)
        else:
            user.create_user()
            replies = conv.handle_conversation(user)

        return conv.send_replies(replies)
    except Exception as e:
        print(f"Error occurred: {e}")
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001)
