import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() #Loading the environment variables

class AIHandler:
    def __init__(self) -> None:
        ai_api_key: str = self.load_openai_api_key()
        self.client = OpenAI(api_key=ai_api_key)
        self.prompts = self.load_prompts()

    def load_openai_api_key(self):
        ai_api_key: str = os.getenv('OPENAI_API_KEY')
        if not ai_api_key:
            raise ValueError("OpenAI API key not found in environment variables.")
        return ai_api_key

    def load_prompts(self):
        with open('./app/data/prompts.json', 'r') as f:
            return json.load(f)

    def generate_response(self, messages, model="gpt-4o-mini", max_tokens=230, temperature=0.7):
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            n=1,
        )
        raw_message = response.choices[0].message.content.strip()
        return raw_message

    def generate_advice(self, category, user_input=None):
        """
        Generates advice based on the selected category.
        """
        # Get the appropriate prompt for the category
        prompt_template = self.prompts["advice_prompts"].get(category, {}).get("prompt", "")

        if not prompt_template:
            raise ValueError(f'No prompt template found for category: {category}')
        
        # Modify the prompt to include formatting instructions
        formatting_instructions = (
            "1. Please provide the advice in clear, concise bullet points suitable for a WhatsApp message. "
            "2.1 Please use emojis to give advice better in this case, either by using it in bullets or heading."
            "2.2 Format your output in bullet points and headings."
            "3. Use whatsapp formatting to ensure the advice looks professional and easy to read." 
            "4. Give advice in sections." 
            "5. The advice should be concise and less than 200 words. or 15 lines of content"
            "6. Avoid using Markdown or HTML formatting. Make the advice engaging and easy to read. Can also add emojis that make it look more professional."
            "7. The final message will be sent to the user and it should be displayed to just show the infomation rather you acknowledging these prompts"
        )

        # Construct the messages
        prompt = prompt_template + formatting_instructions
        messages = [{'role': 'system', 'content': prompt}]

        # If user input is provided, add it to the messages
        if user_input:
            messages.append({'role': 'user', 'content': user_input})

        # Generate the advice using the generate_response method
        advice = self.generate_response(messages, model='gpt-4o-mini', max_tokens=200, temperature=0.7)
        return advice

    def generate_feedback(self, question, user_response):
        # Get the feedback prompt template
        feedback_prompt_template = self.prompts["interview_prompts"]["feedback_prompt"]["prompt"]
        # Modify the prompt to include formatting instructions
        formatting_instructions = (
            "1. Please provide the advice in clear, concise bullet points suitable for a WhatsApp message. "
            "2.1 Please use emojis to give advice better in this case, either by using it in bullets or heading."
            "2.2 Format your output in bullet points and headings."
            "3. Use whatsapp formatting to ensure the advice looks professional and easy to read." 
            "4. Give advice in sections." 
            "5. The advice should be concise and less than 200 words."
            "6. Avoid using Markdown or HTML formatting. Make the advice engaging and easy to read. Can also add emojis that make it look more professional."
            "7. The final message will be sent to the user and it should be displayed to just show the infomation rather you acknowledging these prompts"
        )

        feedback_prompt = feedback_prompt_template + formatting_instructions

        # Construct the messages
        messages = [
            {'role': 'system', 'content': feedback_prompt},
            {'role': 'user', 'content': f"Question: {question}\nUser Response: {user_response}"}
        ]

        # Generate the feedback
        feedback = self.generate_response(messages, model='gpt-4o-mini', max_tokens=500, temperature=0.7)
        return feedback

    def generate_follow_up_question(self, user_response, interview_type, role):
        prompt_template = self.prompts['interview_prompts']['follow_up_prompt']['prompt']
        prompt = prompt_template.format(
            user_response = user_response,
            interview_type = interview_type,
            role = role    
        )
        
        messages = [{'role': 'system', 'content': prompt}]
        follow_up_question = self.generate_response(messages)
        
        return follow_up_question

    def generate_interview_feedback(self, question, user_response, follow_up_question, follow_up_response, interview_type, role):
        prompt_template = self.prompts['interview_prompts']['feedback_prompt']['prompt']
        prompt = prompt_template.format(
            question = question,
            user_response = user_response,
            follow_up_question = follow_up_question,
            follow_up_response = follow_up_response,
            interview_type = interview_type,
            role = role
        )

        messages = [{'role':'system', 'content': prompt}]
        feedback = self.generate_response(messages)

        return feedback
        

    def handle_irrelevant_question(self):
        # Get the irrelevant question prompt
        irrelevant_prompt = self.prompts["irrelevant_question"]["prompt"]

        # Construct the messages
        messages = [{'role': 'system', 'content': irrelevant_prompt}]

        # Generate the response
        response = self.generate_response(messages, model='gpt-4o-mini', max_tokens=100, temperature=0.7)
        return response