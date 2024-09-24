import random
from flask import Flask, request
import requests
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import json

# Reading the message templates
with open('./data/messages.json', 'r') as f:
    messages = json.load(f)

# Select a random question from the list of questions #
def select_random_question(fp: str = './data/questions_college.txt'):
    try: 
        with open(fp, 'r') as f:
            questions: list[str] = f.readlines()

        questions = [question.strip() for question in questions]

        rand_question: str = random.choice(questions)

        return rand_question
    
    except FileNotFoundError:
        return 'Question bank not found'
    except Exception as e:
        return f'Error occured while selecting random question {e}'

# Onboarding messages #
def onboarding_messages(msg):
    onboarding_msgs: list = messages['onboarding']
    message = onboarding_msgs['welcome']
    msg.body(message)
    return None