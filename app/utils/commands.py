

class CommandHandler:
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user

    def check_for_commands(self, user_input):
        commands = ['exit', 'restart', 'options', 'help']
        user_input_clean = user_input.strip().lower()
        if user_input_clean in commands:
            return user_input_clean
        else:
            return None

    def handle_command(self, command):
        to_number = self.user.get_user_number()
        if command == 'exit':
            self.bot.say(to_number, "Thank you for using our service! Goodbye!")
            self.user.set_conversation_stage('onboarded')
        elif command == 'restart':
            self.restart_conversation()
        elif command == 'options':
            self.user.set_conversation_stage('onboarded')
            self.bot.say(to_number, "Returning to options...")
            # Possibly call a method to display options
        elif command == 'help':
            help_message = (
                "You can use the following commands at any time:\n"
                "- 'exit': Quit the chat.\n"
                "- 'restart': Restart the current section of the conversation.\n"
                "- 'options': Go back to the main menu to select interview preparation or general advice.\n"
                "- 'help': Show this help message."
            )
            self.bot.say(to_number, help_message)

    def restart_conversation(self):
        to_number = self.user.get_user_number()
        current_stage = self.user.get_conversation_stage()
        if current_stage in ['awaiting_name', 'initial']:
            self.user.set_conversation_stage('initial')
            self.bot.say(to_number, "Restarting onboarding...")
            # You might need to call methods from Conversation class
        elif current_stage.startswith('awaiting_interview'):
            self.user.set_conversation_stage('awaiting_interview_type')
            self.bot.say(to_number, "Restarting interview preparation...")
        elif current_stage.startswith('awaiting_advice'):
            self.user.set_conversation_stage('awaiting_advice_category')
            self.bot.say(to_number, "Restarting this section...")
        else:
            self.user.set_conversation_stage('onboarded')
            self.bot.say(to_number, "Returning to the main menu...")
