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
        self.from_number : str = self.get_from_number()

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
    def get_from_number(): 
        from_number = os.getenv('TWILIO_FROM_NUMBER')
        return from_number
    
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

    def send_reply(self, user, body):
        """Send a message using the Twilio client."""
        to_number = user.get_user_number()
        print(to_number)
        message = self.twilio_client.messages.create(
            from_='whatsapp:' + self.from_number,
            to='whatsapp:' + to_number,
            body=body
        )
        print(f"Message sent with SID: {message.sid}")
    
    def send_sequence(self, user, sequence):
        # TODO: Create a function that sends sequences
        pass
    
    def ask_purpose(self, user):
        welcome_back_msgs = self.messages['welcome_back']
        options_message = welcome_back_msgs['options']
        self.send_reply(user, options_message)

        # Set the user's right conversation_stage
        user.set_conversation_stage('awaiting-purpose')
        return
    # Onboarding Function #    
    def onboarding(self, user, current_stage):
        """Handle the onboarding sequence for a new user."""
        onboarding_msgs = self.messages['onboarding']

        if current_stage == 'initial':
            # Send welcome message and ask for the user's name
            welcome_message = onboarding_msgs['welcome']
            ask_name_message = onboarding_msgs['ask_name']

            # Send onboarding messages
            self.send_reply(user, welcome_message)
            self.send_reply(user, ask_name_message)

            # Set conversation stage to 'awaiting_name'
            user.set_conversation_stage('awaiting_name')

            return

        elif current_stage == 'awaiting_name':
            # Wait for the user's reply (which should be their name)
            user_reply = request.form.get('Body')
            # Todo: Add a validation function to validate name

            # Extract the user's name from their reply
            user_name = user_reply.strip()
            user.update_user_name(user_name) # Update User Name

            # Confirm the name and provide options
            confirm_name_message = onboarding_msgs['confirm_name'].format(name=user_name)
            options_message = onboarding_msgs['options']
            # Todo: Replace this with the quick_option()
            # Send the messages
            # Todo: Add a logging function to log this
            self.send_reply(user, confirm_name_message)
            self.ask_purpose(user)
            return

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

        # Send the welcome back message
        self.send_reply(user, greeting_message)
        self.ask_purpose(user)
    
    # Ask a question
    def ask_question(self) -> str:
        question = self.select_random_question()
        return f"Here's a question for you: {question}"
    
    def define_purpose(self, user):
        # Get the user's reply (either number or text)
        reply = request.form.get('Body', '').strip().lower()  # Strip spaces and convert to lowercase for consistency

        # Determine the purpose based on reply
        if reply in ['1', 'interview preparation', 'interview practice']:
            purpose = 'interview_preparation'
            body = "You've selected Interview Preparation. We will begin shortly."
        elif reply in ['2', 'general advice']:
            purpose = 'general_advice'
            body = "You've selected General Advice. Please wait while we gather the necessary information."
        else:
            purpose = 'unknown'
            body = "Sorry, I couldn't understand your selection. Please reply with 1 for Interview Preparation or 2 for General Advice."

        # Send confirmation message to the user
        self.send_reply(user, body)

        # Update the conversation stage with the determined purpose
        user.set_conversation_stage(purpose)
    def interview(self, user):
        pass

    def handle_conversation(self, user) -> list:
        """Handle user conversation flow based on their current stage."""
        current_stage = user.get_conversation_stage()
        # Handle user interaction based on the stage
        if current_stage == 'initial':
            self.onboarding(user, current_stage)
        elif current_stage == 'awaiting_name':
            self.onboarding(user, current_stage)
        elif current_stage == 'onboarded':
            self.welcome_back(user)
        elif current_stage == 'awaiting-purpose':
            self.define_purpose(user)
        elif current_stage == 'interview-preperation':
            self.interview(user)
        elif current_stage == 'interview-followup':
            self.interview_followup(user)
        elif current_stage == 'general-advice':
            self.advice(user)
        elif current_stage == 'advice-followup':
            self.advice_followup(user)
        else:
            # For existing users, proceed with the welcome back sequence
            self.welcome_back(user)
        
    def conversation_reset(self, user):
        # TODO: Create a function that will reset the conversation
        pass