import random
import json

class Question:
    def __init__(self, question_fp: str = './data/questions.json'):
        self.question_fp = question_fp
        self.questions = self.load_questions()

    # Load questions from the specified file
    def load_questions(self) -> list[str]:
        try:
            with open(self.question_fp, 'r') as f:
                questions = json.load(f)

            return questions.get("questions", [])
        except FileNotFoundError:
            print('Question bank not found.')
            return []
        except Exception as e:
            print(f'Error occurred while loading questions: {e}')
            return []

    # Select a random question from the list
    def select_random_question(self) -> str:
        if self.questions:
            return random.choice(self.questions)
        else:
            return 'No questions available.'