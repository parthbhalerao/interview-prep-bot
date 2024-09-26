from flask import request
from bot import Bot
from utils.user import User
import json

class Conversation:
    def __init__(self, user):
        self.messages = self.load_messages()
        self.bot = Bot()
        self.user = user

    @staticmethod
    def load_messages():
        """Load messages from JSON."""
        with open('./app/data/messages.json') as f:
            return json.load(f)

    def handle_conversation(self):
        """Main method to handle conversation flow."""
        current_stage = self.user.get_conversation_stage()
        print(f"Handling conversation at stage: {current_stage}")
        
        if current_stage == 'initial':
            self.onboarding(self.user)
        elif current_stage == 'awaiting_name':
            self.onboarding(self.user)
        elif current_stage == 'onboarded':
            self.welcome_back(self.user)
        elif current_stage == 'awaiting_purpose':
            self.define_purpose(self.user)
        elif current_stage == 'interview_preparation':
            self.handle_interview(self.user)
        elif current_stage == 'general_advice':
            self.provide_general_advice(self.user)
        else:
            self.welcome_back(self.user)

    def onboarding(self, user):
        """Onboarding sequence for new users."""
        to_number = user.get_user_number()
        current_stage = user.get_conversation_stage()

        onboarding_msgs = self.messages['onboarding']

        if current_stage == 'initial':
            welcome_message = onboarding_msgs['welcome']
            ask_name_message = onboarding_msgs['ask_name']
            
            # Use the Bot class to send messages
            self.bot.say(to_number, welcome_message)
            self.bot.say(to_number, ask_name_message)

            user.set_conversation_stage('awaiting_name')

        elif current_stage == 'awaiting_name':
            user_reply = request.form.get('Body').strip()
            user_name = user_reply  # Optionally, add name validation

            # Update the user's name
            user.update_user_name(user_name)

            confirm_name_message = onboarding_msgs['confirm_name'].format(name=user_name)
            self.bot.say(to_number, confirm_name_message)

            # Updates the user's conversation_stage
            user.set_conversation_stage('onboarded')

            self.ask_purpose(self.user)

    def ask_purpose(self, user):
        """Ask user for their purpose (e.g., interview preparation, general advice)."""
        to_number = user.get_user_number()
        welcome_back_msgs = self.messages['welcome_back']
        options_message = welcome_back_msgs['options']

        # Use the Bot class to send the options message
        self.bot.ask(to_number, options_message)

        # Update the user's conversation stage
        user.set_conversation_stage('awaiting_purpose')

    def define_purpose(self, user):
        """Determine the user's purpose based on their reply."""
        to_number = user.get_user_number()
        reply = request.form.get('Body', '').strip().lower()

        if reply in ['1', 'interview preparation', 'interview practice']:
            purpose = 'interview_preparation'
            body = "You've selected Interview Preparation. We will begin shortly."
        elif reply in ['2', 'general advice']:
            purpose = 'general_advice'
            body = "You've selected General Advice. Please wait while we gather the necessary information."
        else:
            purpose = 'awaiting_purpose'
            body = "Sorry, I couldn't understand your selection. Please reply with 1 for Interview Preparation or 2 for General Advice."

        # Send confirmation and set the conversation stage
        self.bot.say(to_number, body)
        user.set_conversation_stage(purpose)

    def welcome_back(self, user):
        """Handle the welcome back sequence for returning users."""
        to_number = user.get_user_number()
        welcome_back_msgs = self.messages['welcome_back']

        user_info = user.get_user_info()
        if not user_info:
            self.bot.say(to_number, "We couldn't find your information. Please start by saying 'Hello'.")
            return

        user_name = user_info[1] if user_info[1] else 'User'
        greeting_message = welcome_back_msgs['greeting'].format(name=user_name)

        self.bot.say(to_number, greeting_message)
        self.ask_purpose(user)

    def handle_interview(self, user):
        """Handle interview preparation logic."""
        to_number = user.get_user_number()
        interview_message = "Let's start your interview preparation."

        self.bot.say(to_number, interview_message)
        # Further logic for interview preparation can be added here

    def provide_general_advice(self, user):
        """Handle general advice logic."""
        to_number = user.get_user_number()
        advice_message = "Here's some general advice for you."

        self.bot.say(to_number, advice_message)
        # Further logic for general advice can be added here
