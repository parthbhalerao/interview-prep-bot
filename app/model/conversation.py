from flask import request
from model.bot import Bot
from model.ai import AIHandler
from utils.user import User
import json

class Conversation:
    def __init__(self, user):
        self.messages = self.load_messages()
        self.bot = Bot()
        self.user = user
        self.ai = AIHandler()

    @staticmethod
    def load_messages():
        """Load messages from JSON."""
        with open('./app/data/messages.json') as f:
            return json.load(f)

    def handle_conversation(self):
        """Main method to handle conversation flow."""
        current_stage = self.user.get_conversation_stage()
        print(f"Handling conversation at stage: {current_stage}")
        
        if current_stage in ['initial', 'awaiting_name']:
            self.onboarding(self.user)
        elif current_stage == 'onboarded':
            self.welcome_back(self.user)
        elif current_stage == 'awaiting_purpose':
            self.define_purpose(self.user)
        elif current_stage == 'awaiting_advice_category':
            self.define_advice_category(self.user)
        elif current_stage == 'awaiting_advice_followup':
            self.handle_advice_followup(self.user)
        elif current_stage == 'awaiting_more_advice_followup':
            self.handle_more_advice_followup(self.user)
        elif current_stage == 'awaiting_more_advice':
            self.handle_more_advice(self.user)
        elif current_stage == 'awaiting_interview_input':
            self.handle_interview(self.user)
        else:
            # Reset to onboarded stage in case of an unknown stage
            self.user.set_conversation_stage('onboarded')
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
        self.bot.say(to_number, options_message)

        # Update the user's conversation stage
        user.set_conversation_stage('awaiting_purpose')

    def define_purpose(self, user):
        """Determine the user's purpose based on their reply."""
        to_number = user.get_user_number()
        reply = request.form.get('Body', '').strip().lower()

        if reply in ['1', 'interview preparation', 'interview practice']:
            user.set_conversation_stage('awaiting_interview_input')
            self.start_interview(user)
        elif reply in ['2', 'general advice']:
            user.set_conversation_stage('awaiting_advice_category')
            self.ask_advice_category(user)
        else:
            body = "Sorry, I couldn't understand your selection. Please reply with 1 for Interview Preparation or 2 for General Advice."
            self.bot.say(to_number, body)
            # Remain in the same stage

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
        # Update conversation stage to 'onboarded'
        user.set_conversation_stage('onboarded')
        self.ask_purpose(user)

    def start_interview(self, user):
        """Initiate interview preparation."""
        to_number = user.get_user_number()
        interview_message = "Let's start your interview preparation. Please tell me the role you're applying for."
        self.bot.say(to_number, interview_message)
        # Further logic for interview preparation can be added here

    def handle_interview(self, user):
        """Handle interview preparation logic."""
        to_number = user.get_user_number()
        # Implement logic to handle interview input from the user
        # For simplicity, we'll reset the conversation here
        self.bot.say(to_number, "Interview preparation is under development.")
        # Reset to onboarded stage
        user.set_conversation_stage('onboarded')
        self.ask_purpose(user)

    def ask_advice_category(self, user):
        to_number = user.get_user_number()
        welcome_back_msgs = self.messages['welcome_back']
        select_category_msg = welcome_back_msgs['select_category']

        # Send the select_category_msg to confirm what advice?
        self.bot.say(to_number, select_category_msg)
        user.set_conversation_stage('awaiting_advice_category')

    def define_advice_category(self, user):
        to_number = user.get_user_number()

        # Get the user reply
        reply = request.form.get('Body', '').strip().lower()

        # Mapping the advice_categories
        advice_categories = {
            '1': 'general_tips',
            '2': 'pre_interview_preparation',
            '3': 'behavioral_interview_tips',
            '4': 'virtual_phone_interview_advice',
            '5': 'post_interview_tips'
        }
        if reply in advice_categories:
            # Get the corresponding category
            category = advice_categories[reply]

            # Give advice based on the selected category
            self.give_advice(user, category)
        else:
            # Handle invalid input
            error_message = "Sorry, I didn't understand that. Please reply with a number between 1 and 5."
            self.bot.say(to_number, error_message)
            # Remain in the same stage

    def give_advice(self, user, category):
        """Handle general advice logic."""
        to_number = user.get_user_number()
        advice_message = self.ai.generate_advice(category)
        self.bot.say(to_number, advice_message)
        
        # Store the last advice given for follow-up questions
        user.set_last_advice(advice_message)
        
        # Ask if the user has any questions about the advice
        follow_up_message = "Do you have any questions about this advice? Please feel free to ask or reply 'no' to continue."
        self.bot.say(to_number, follow_up_message)
        
        # Update the conversation stage to await user's follow-up question
        user.set_conversation_stage('awaiting_advice_followup')


    def handle_advice_followup(self, user):
        to_number = user.get_user_number()
        user_question = request.form.get('Body', '').strip()

        if user_question.lower() in ['no', 'n']:
            # User does not have any questions, ask if they need advice on another topic
            self.bot.say(to_number, "Would you like advice on another topic? Reply 'yes' or 'no'.")
            user.set_conversation_stage('awaiting_more_advice')
        else:
            # User has a question, generate a response
            # Retrieve the last advice given
            last_advice = user.get_last_advice()
            
            # Construct the messages
            messages = [
                {'role': 'system', 'content': (
                    "You are a helpful assistant that provides advice and answers follow-up questions. "
                    "When answering, provide clear and concise information suitable for a WhatsApp message. "
                    "Use simple formatting and avoid Markdown or HTML."
                )},
                {'role': 'assistant', 'content': last_advice},
                {'role': 'user', 'content': user_question}
            ]
            
            # Generate the response
            response = self.ai.generate_response(messages, model='gpt-4o-mini', max_tokens=500, temperature=0.7)
            self.bot.say(to_number, response)
            
            # Ask if the user has more questions
            self.bot.say(to_number, "Do you have any more questions about this advice? Reply 'yes' or 'no'.")
            user.set_conversation_stage('awaiting_more_advice_followup')


    def handle_more_advice(self, user):
        to_number = user.get_user_number()
        reply = request.form.get('Body', '').strip().lower()
        
        if reply in ['yes', 'y']:
            self.ask_advice_category(user)
        elif reply in ['no', 'n']:
            closing_message = "Thank you for using our service! If you need anything else, just send a message."
            self.bot.say(to_number, closing_message)
            # Reset conversation stage to onboarded
            user.set_conversation_stage('onboarded')
        else:
            error_message = "Sorry, I didn't understand that. Please reply with 'yes' or 'no'."
            self.bot.say(to_number, error_message)
            # Remain in the same stage

    def handle_more_advice_followup(self, user):
        to_number = user.get_user_number()
        reply = request.form.get('Body', '').strip().lower()
        
        if reply in ['yes', 'y']:
            # User has more questions
            self.bot.say(to_number, "Please ask your question.")
            user.set_conversation_stage('awaiting_advice_followup')
        elif reply in ['no', 'n']:
            # Ask if they need advice on another topic
            self.bot.say(to_number, "Would you like advice on another topic? Reply 'yes' or 'no'.")
            user.set_conversation_stage('awaiting_more_advice')
        else:
            error_message = "Sorry, I didn't understand that. Please reply with 'yes' or 'no'."
            self.bot.say(to_number, error_message)
            # Remain in the same stage

