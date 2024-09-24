import json
from twilio.twiml.messaging_response import MessagingResponse
from utils.helper import User
from flask import request
import os

# Load the messages from json
def load_messages():
    with open('./app/data/messages.json') as f:
        messages = json.load(f)
        return messages

def get_reply():
    # TODO: Create a function that gets the reply from the user
    reply : str = request.value.get('Body', '').lower()
    return reply

def extract_number(request):
    # TODO: Creae a function that gets sender number
    user_number : str = request.form.get('From')
    user_number : str = user_number.split(':')[1]
    return user_number

def send_reply(body):
    bot_rsp = MessagingResponse()
    msg = bot_rsp.message()
    msg.body(body)

def create_twilio_client():
    ACCOUNT_SID : str = os.getenv('ACCOUNT_SID')
    AUTH_TOKEN  : str = os.getenv('AUTH_TOKEN')

def add_reply(reply):
    pass

def extract_name(reply : str):
    # TODO: Creae a function that gets name from the user
    pass

def onboarding(user, user_msg):
    # Load onboarding messages
    messages = load_messages()
    onboarding_msgs = messages['onboarding']

    # Create a new user in the database
    user.create_user()

    # Send a introduction message
    welcome_message = onboarding_msgs['welcome']
    send_reply(welcome_message)

    # Send asking for name message

    # Wait for the user to reply with name

    # Extract the name from the message

    # Create the user 

    # Reply with Options that they can take after this

welcome_message = onboarding()
print(welcome_message)




