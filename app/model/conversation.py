from flask import request
from model.bot import Bot
from model.ai import AIHandler
from utils.user import User
from utils.commands import CommandHandler
import json
import random

class Conversation:
    def __init__(self, user):
        self.messages = self.load_messages()
        self.interview_questions = self.load_interview_questions()
        self.bot = Bot()
        self.user = user
        self.ai = AIHandler()
        self.command_handler = CommandHandler(self.bot, self.user)

    @staticmethod
    def load_messages():
        """Load messages from JSON."""
        with open('./app/data/messages.json') as f:
            data = json.load(f)
            return data  # Return the entire messages dictionary


    @staticmethod
    def load_interview_questions():
        with open('./app/data/questions.json') as f:
            data = json.load(f)
            # Extract the list of questions
            interview_questions = [item['question'] for item in data['behavioral_questions']]
            return interview_questions


    def handle_conversation(self):
        """Main method to handle conversation flow."""
        user_input = request.form.get('Body', '').strip()  # Read reply
        
        command = self.command_handler.check_for_commands(user_input)
        if command:
            print(f'Command: {command} detected in reply. Handling it.')
            self.command_handler.handle_command(command)
            return  # Exit after handling the command
        
        else:
            current_stage = self.user.get_conversation_stage()
            print(f"Handling conversation at stage: {current_stage}")
            
            # Initiating the conversation
            if current_stage in ['initial', 'awaiting_name']:
                self.onboarding(self.user)
            elif current_stage == 'onboarded':
                self.welcome_back(self.user)
            elif current_stage == 'awaiting_purpose':
                self.define_purpose(self.user)

            # Handle Interview Sessions
            elif current_stage == 'awaiting_interview_type':
                self.get_interview_type(self.user)
            elif current_stage == 'awaiting_interview_role':
                self.get_interview_role(self.user)
            elif current_stage == 'awaiting_interview_question_response':
                self.capture_interview_response(self.user)
            elif current_stage == 'awaiting_follow_up_response':
                self.capture_follow_up_response(self.user)
            elif current_stage == 'awaiting_more_interview':
                self.handle_more_interview(self.user)

            # Handle General Advice Sessions
            elif current_stage == 'awaiting_advice_category':
                self.define_advice_category(self.user)
            elif current_stage == 'awaiting_advice_followup':
                self.handle_advice_followup(self.user)
            elif current_stage == 'awaiting_more_advice_followup':
                self.handle_more_advice_followup(self.user)
            elif current_stage == 'awaiting_more_advice':
                self.handle_more_advice(self.user)

            # Handle unkown sessions    
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
            print('Starting onboarding')
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
            print('Finished onboarding %s' % user_name)

            # Updates the user's conversation_stage
            user.set_conversation_stage('onboarded')
            self.ask_purpose(self.user)

    def welcome_back(self, user):
        """Handle the welcome back sequence for returning users."""
        to_number = user.get_user_number()
        welcome_back_msgs = self.messages['welcome_back']

        user_info = user.get_user_info()
        if not user_info:
            self.bot.say(to_number, "We couldn't find your information. Please start by saying 'Hello'.")
            return

        user_name = user.get_user_name()
        greeting_message = welcome_back_msgs['greeting'].format(name=user_name)

        self.bot.say(to_number, greeting_message)
        # Update conversation stage to 'onboarded'
        user.set_conversation_stage('onboarded')
        self.ask_purpose(user)    

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
            user.set_conversation_stage('awaiting_interview_type')
            self.ask_interview_type(user)
        elif reply in ['2', 'general advice']:
            user.set_conversation_stage('awaiting_advice_category')
            self.ask_advice_category(user)
        else:
            body = "Sorry, I couldn't understand your selection. Please reply with 1 for Interview Preparation or 2 for General Advice."
            self.bot.say(to_number, body)
            # Remain in the same stage

    #################################
    # Interview Preparation Methods # 
    #################################
    def ask_interview_type(self, user):
        to_number = user.get_user_number()
        message = "Are you preparing for a college interview or a job interview? Please reply with 'college' or 'job'."
        self.bot.say(to_number, message)
        user.set_conversation_stage('awaiting_interview_type')

    def get_interview_type(self, user):
        interview_type = request.form.get('Body', '').strip().lower()

        if interview_type in ['college', 'job']:
            user.set_interview_type(interview_type)

            self.ask_interview_role(user)

    def ask_interview_role(self, user):
        to_number = user.get_user_number()
        interview_type = user.get_interview_type()

        if interview_type == 'college':
            message = "Please specify the college or program you're applying to so I can tailor the interview questions accordingly."
        else:  # 'job'
            message = "Please specify the job role you're applying for so I can tailor the interview questions accordingly."
        self.bot.say(to_number, message)
        user.set_conversation_stage('awaiting_interview_role')


    def get_interview_role(self, user):
        to_number = user.get_user_number()

        role = request.form.get('Body', '').strip().upper()
        user.set_interview_role(role)

        interview_type = user.get_interview_type()
        if interview_type == 'college':
            message = f"Great! Let's start the interview for {role}."

        else: # job
            message = f"Great! Let's start the interview for a {role} position."
            
        self.bot.say(to_number, message)
        self.ask_interview_question(user)

    def ask_interview_question(self, user):
        to_number = user.get_user_number()
        interview_type = user.get_interview_type()
        last_interview_question = user.get_last_interview_question()

        question = random.choice(self.interview_questions)
        
        if question == last_interview_question:
            question = 

        if interview_type == 'college':

        user.set_last_interview_question(question)

        # Ask the question
        self.bot.say(to_number, question)
        user.set_conversation_stage('awaiting_interview_question_response')

    def capture_interview_response(self, user):
        user_reponse = request.form.get('Body', '').strip()
        user.set_interview_response(user_reponse)

        # Generate a follow up
        self.generate_follow_up_question(user)

    def generate_follow_up_question(self, user):
        user_response = user.get_last_interview_response()
        interview_type = user.get_interview_type()
        role = user.get_interview_role()

        follow_up_question = self.ai.generate_follow_up_question(user_response, interview_type, role)
        user.set_last_follow_up_question(follow_up_question)
        
        to_number = user.get_user_number()
        self.bot.say(to_number, follow_up_question)
        
        user.set_conversation_stage('awaiting_follow_up_response')

    def capture_follow_up_response(self, user):
        to_number = user.get_user_number()
        follow_up_response = request.form.get('Body', '').strip()
        
        user.set_follow_up_response(follow_up_response)

        self.provide_feedback(user)

    def provide_feedback(self, user):
        to_number = user.get_user_number()
        question = user.get_last_interview_question()
        user_response = user.get_last_interview_response()
        follow_up_question = user.get_last_follow_up_question()
        follow_up_response = user.get_last_follow_up_response()
        interview_type = user.get_interview_type()
        role = user.get_interview_role()
        print(f'Successfully got background for feedback')
        
        feedback = self.ai.generate_interview_feedback(question,user_response, follow_up_question, follow_up_response, interview_type, role)

        self.bot.say(to_number, feedback)

        self.bot.say(to_number, "Would you like to practice another question? Reply 'yes' or 'no'.")
        user.set_conversation_stage('awaiting_more_interview')

    def handle_more_interview(self, user):
        to_number = user.get_user_number()
        reply = request.form.get('Body', '').strip().lower()

        if reply in ['yes', 'y']:
            self.ask_interview_question(user)
        elif reply in ['no', 'n']:
            self.bot.say(to_number, "Thank you for practicing. Start another conversation by sending another message.")
            user.set_conversation_stage('onboarded')
        else:
            error_message = "Sorry, I didn't understand that. Please reply with 'yes' or 'no'."
            self.bot.say(to_number, error_message)
            # Remain in the same stage

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

    ##########################
    # General Advice Methods #
    ##########################
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

