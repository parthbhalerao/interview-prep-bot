import json
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from utils.helper import User
from flask import request
import os

class Conversation():
    def __init__(self):
        self.messages = self.load_messages()
        self.twilio_client = self.create_twilio_client()

    @staticmethod
    def load_messages():
        """Load messages"""
        with open('./app/data/messages.json') as f:
            messages = json.load(f)
            return messages

    @staticmethod
    def create_twilio_client():
        """Create Twilio Client instance"""
        account_sid : str = os.getenv('ACCOUNT_SID')
        auth_token : str = os.getenv('AUTH_TOKEN')
        return Client(account_sid, auth_token)
    
    @staticmethod
    def get_reply():
        # TODO: Create a function that gets the reply from the user
        reply : str = request.form.get('Body', '').lower()
        return reply

    @staticmethod
    def extract_number():
        # TODO: Creae a function that gets sender number
        user_number : str = request.form.get('From')
        user_number : str = user_number.split(':')[1]
        return user_number

    @staticmethod
    def extract_name(reply : str):
            name = reply.split()[0]
            return name

    def send_reply(self, body):
        bot_rsp = MessagingResponse()
        msg = bot_rsp.message()
        msg.body(body)

    def add_reply(self, replies):
        bot_rsp = MessagingResponse()
        for reply in replies:
            msg = bot_rsp.message()
            msg.body(reply)
        return str(bot_rsp)

    def onboarding(self, user):
        """Handle the onboarding sequence for a new user."""
        onboarding_msgs = self.messages['onboarding']
        
        # Check the user's current conversation stage
        current_stage = user.get_conversation_stage()

        if current_stage == 'initial':
            # Send welcome message and ask for the user's name
            welcome_message = onboarding_msgs['welcome']
            ask_name_message = onboarding_msgs['ask_name']

            # Set conversation stage to 'awaiting_name'
            user.set_conversation_stage('awaiting_name')

            # Return the replies to send
            return [welcome_message, ask_name_message]

        elif current_stage == 'awaiting_name':
            # Wait for the user's reply (which should be their name)
            user_reply = request.form.get('Body')

            # Extract the user's name from their reply
            user_name = user_reply.strip()  # Assuming the reply is the user's name
            user.update_user_name(user_name)

            # Confirm the name and provide options
            confirm_name_message = onboarding_msgs['confirm_name'].format(name=user_name)
            options_message = onboarding_msgs['options']

            # Set conversation stage to 'onboarded' after receiving name
            user.set_conversation_stage('onboarded')

            # Return confirmation and options
            return [confirm_name_message, options_message]

    def welcome_back(self, user):
        """Handle the welcome back sequence for returning users."""
        welcome_back_msgs = self.messages['welcome_back']

        # Fetch user information and handle case where user doesn't exist
        user_info = user.get_user_info()

        if not user_info:
            # Handle case where user is not found in the database
            return ["We couldn't find your information. Please start the onboarding process by saying 'Hello'."]

        user_name = user_info[1] if user_info[1] else 'User'  # Default to 'User' if no name

        # Send the welcome back message
        greeting_message = welcome_back_msgs['greeting'].format(name=user_name)
        options_message = welcome_back_msgs['options']

        # Return the greeting and options
        return [greeting_message, options_message]

    def handle_conversation(self, user):
        """Handle user conversation flow based on their current stage."""
        current_stage = user.get_conversation_stage()
        # Handle user interaction based on the stage
        if current_stage == 'initial':
            return self.onboarding(user)
        elif current_stage == 'awaiting_name':
            return self.onboarding(user)
        else:
            # For existing users, proceed with the welcome back sequence
            return self.welcome_back(user)

    def send_replies(self, replies):
        """Helper function to send multiple replies using Twilio MessagingResponse."""
        bot_resp = MessagingResponse()
        for reply in replies:
            msg = bot_resp.message()
            msg.body(reply)
        return str(bot_resp)