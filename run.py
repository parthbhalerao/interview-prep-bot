from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Initialize the Flask Application
app = Flask(__name__)

@app.route('/')
def home():
    return "Flask app is running"

@app.route('/whatsapp', methods=['POST'])
def bot():
    # Get the user's message from the request sent by Twilio
    user_msg: str = request.values.get('Body', '').lower()

    # Initialize Twilio's Messaging Response
    bot_resp = MessagingResponse()
    msg = bot_resp.message()

    # Respond to specific messages
    if 'hello' in user_msg:
        msg.body('Hello')

    elif 'help' in user_msg:
        msg.body("How can I assist you? You can ask me about college interview tips, practice questions, or anything else!")
    else:
        msg.body(f"You said: {user_msg}. I'm still learning, but feel free to ask me about college interviews!")

    return str(bot_resp)

# Running the Flask App
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5001, debug=True)

