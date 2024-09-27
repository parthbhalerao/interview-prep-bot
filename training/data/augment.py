import json
import random
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

class DataAugmentor:
    def __init__(self, model_name='llama3.1', purpose = 'data augmentation', questions_fp : str = 'training/data/interview_questions.json'):
        self.model =OllamaLLM(model=model_name)
        self.purpose = purpose
        self.questions_fp = questions_fp
        self.gen_question_prompt = self.create_question_prompt()
        self.gen_answer_prompt = self.create_answer_prompt()
        self.gen_feedback_prompt = self.create_feedback_prompt()
        self.user_backgrounds = self.create_user_backgrounds()

    def create_question_prompt(self):
        template = (
            "You are an expert in behavioral interviews. Please provide {num_variations} different variations of the following interview question."
            "The variations should be similar but ask the question in different ways, while still focusing on the same topic.\n\n"
            "Original Question: '{question}'\n\n"
            "Variations:"
        )
        return ChatPromptTemplate.from_template(template)
    
    def create_answer_prompt(self):
        template = (
            "You are an expert interview coach. Generate an ideal answer to the following behavioral interview question using the STAR (Situation, Task, Action, Result) method. "
            "The answer should be detailed, realistic, and mimic a verbal response in an interview setting. The respondent is {user_background}.\n\n"
            "Question: '{question}'\n\n"
            "Answer:"
        )
        return ChatPromptTemplate.from_template(template)

    def create_feedback_prompt(self):
        template = (
            "You are an expert interview coach engaging in a conversation with {user_background}. The user has provided an answer to an interview question. "
            "Provide detailed feedback on their answer, highlighting strengths and areas for improvement. Then, ask a relevant follow-up question to engage the user in further conversation.\n\n"
            "User's Answer: '{user_answer}'\n\n"
            "Assistant:"
        )
        return ChatPromptTemplate.from_template(template)

    def create_user_backgrounds(self):
        # Define some example user backgrounds for variation in answers, including first-generation Americans
        return [
            # General professional backgrounds
            "a recent college graduate with a degree in computer science",
            "a project manager with 5 years of experience in the tech industry",
            "a mid-career professional transitioning into a data science role",
            "a software engineer with 3 years of experience in machine learning",
            "a business analyst with a strong background in finance and analytics",
            "a marketing manager with experience in digital campaigns and client acquisition",
            "a recent MBA graduate specializing in business strategy and operations",
            "a data scientist with expertise in machine learning and statistical analysis",
            "a product manager with 7 years of experience in the e-commerce industry",
            "a human resources professional with a focus on organizational development",
            "a software developer transitioning into an engineering leadership role",
            "a customer service representative with experience managing high-volume client interactions",

            # First-generation American backgrounds for college admissions help
            "a first-generation American high school student looking for guidance on college admissions",
            "a first-generation American student aiming to get into a top-tier university and needs advice on college essays",
            "a first-generation American student from a low-income family who needs help navigating financial aid for college",
            "a first-generation immigrant student applying to colleges and seeking help with scholarship opportunities",
            "a high school student who is the first in their family to apply for college and needs support in choosing the right major",
            "a first-generation American student preparing for college interviews and essay submissions",
            "a first-generation American student interested in STEM but unsure how to approach college admissions",
            "a first-generation student from a non-English speaking household needing help with the overall college admissions process",
            "a first-generation American high schooler with no family history of higher education looking for college admissions guidance",
            "a first-generation student balancing part-time work and school, seeking advice on how to present their unique story in college applications"
        ]

    def load_questions(self):
        with open(self.questions_fp) as f:
            questions_data = json.load(f)
            questions = questions_data['behavioral_questions']

            return questions

    def select_random_background(self) -> str:
        user_background = random.choice(self.user_backgrounds)
        return user_background
    
    def gen_question_variations(self, question : str, num_variations = 5):
        variations : list[str] = [] # Strore the variants to this list
        variations.append(question)

        filled_prompt = self.gen_question_prompt.format(
            question = question,
            num_variations = num_variations
        )
        
        try:
            question_variations = self.model.invoke(filled_prompt).strip()
            print(f'Generated Question Variations: {question_variations}')
            new_variations = question_variations.split('\n')
            for variation in new_variations:
                variations.append(variation)
            return variations
        except Exception as e:
            print(f'Error generating new Question Variations: {e}')
            return [question]

    def gen_user_answer(self, question):
        user_background : str = self.select_random_background()

        filled_prompt = self.gen_answer_prompt.format(
            question = question,
            user_background = user_background
        )
         # TODO: Complete this function
        try:
            user_answer = self.model.invoke(filled_prompt).strip()
            print(f'Generated User answer: {user_answer}')
            return user_answer
        except Exception as e:
            print(f'Error generating user answer: {e}')
            return None
    
    def gen_feedback(self, user_answer, user_background):
        filled_prompt = self.gen_feedback_prompt.format(
            user_answer=user_answer,
            user_background=user_background
        )

        try:
            feedback = self.model.invoke(filled_prompt).strip()
            print(f'Generated Feedback: {feedback}')
            return feedback
        except Exception as e:
            print(f'Error generating feedback: {e}')
            return None

    def gen_train_data(self, output_fp: str, num_variations=5):
        # Load the questions
        questions = self.load_questions()
        print('Loaded sample data -> environment')
        alpaca_format_data = []
        print('Created alpaca format data list -> empty list')

        for question in questions:
            # Generate variations of the question
            question_variations = self.gen_question_variations(question, num_variations)
            print('Generated variations of the question')

            for variant in question_variations:
                # For each variation, generate a user answer
                user_answer = self.gen_user_answer(variant)
                print('User answer generated for the variation.')
                if user_answer:
                    # Generate feedback for the user answer
                    user_background = self.select_random_background()
                    print('Random background for the user selected for the variation')
                    feedback = self.gen_feedback(user_answer, user_background)
                    print('Generated feedback for the variation')

                    alpaca_format_data.append({
                        'instruction': variant,
                        'input': '',  # You can add context if needed, or leave it empty
                        'output': user_answer,
                        'feedback': feedback  # Add the feedback to the dataset
                    })

        # Save the generated dataset to the specified file in Alpaca format
        try:
            with open(output_fp, 'w') as f:
                json.dump(alpaca_format_data, f, indent=4)
            print(f"Training dataset successfully saved in Alpaca format to {output_fp}")
        except Exception as e:
            print(f"Error saving training data: {e}")

if __name__ == "__main__":
    output_fp = "augmented_interview_data_alpaca_format.json"  # Output file for the Alpaca-formatted dataset
    augmentor = DataAugmentor()  # Instantiate your DataAugmentor class
    augmentor.gen_train_data(output_fp=output_fp, num_variations=5)  # Generate the dataset
