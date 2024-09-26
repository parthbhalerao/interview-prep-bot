import os
from twilio.rest import Client

class Bot:
    def __init__(self):
        self.twilio_client = self.create_twilio_client()
        self.from_number = self.get_from_number()

    @staticmethod
    def create_twilio_client():
        """Create Twilio Client instance"""
        account_sid = os.getenv('ACCOUNT_SID')
        auth_token = os.getenv('AUTH_TOKEN')
        return Client(account_sid, auth_token)

    @staticmethod
    def get_from_number():
        return os.getenv('TWILIO_FROM_NUMBER')

    def say(self, to_number : str, message_body : str):
        """Send a message to the specified number."""
        message = self.twilio_client.messages.create(
            from_='whatsapp:' + self.from_number,
            to='whatsapp:' + to_number,
            body=message_body
        )
        print(f"Message sent to {to_number} with SID: {message.sid}")

    def ask(self, to_number : str, question : str):
        """Send a question to the user."""
        self.say(to_number, question)

    def send_sequence_to(self, to_number : str, message_list : list):
        """Send a sequence of messages to the user."""
        for message in message_list:
            self.say(to_number, message)
