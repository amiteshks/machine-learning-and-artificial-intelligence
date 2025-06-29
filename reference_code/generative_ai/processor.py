""" 
*** Set up the environment ***
    python3 -m venv venv
    % python3 -m venv venv
    pip install openai


*** Store key in the .env file
    pip install python-dotenv


"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

class Processor:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env")

        # print (api_key_1)    
        print (api_key)

        self.client = OpenAI(api_key=api_key)



    def chatbot_process(self, user_message: str):
        print(f"user message: {user_message}")


        response = self.client.chat.completions.create(
            model="gpt-4.1-nano",  # Change to a model you have access to
            messages=[
                {"role": "system", "content": "You are an AI agent. "},
                {"role": "user", "content": user_message}
            ]
        )

        return response.choices[0].message.content


if __name__ == '__main__':
    test_message = "When was Covid detected?"
    processor = Processor()
    response = processor.chatbot_process(test_message)
    print(f"response: {response}")
