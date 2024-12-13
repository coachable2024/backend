import os
from typing import List

import openai
# import instructor
from dotenv import load_dotenv

from metadata import (IntentSystemPrompt, GoalSettingSystemPrompt, 
                      coachName2assistantPrompt)
from data_model import Goal, ChatInput

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# instructor_client = instructor.from_openai(client)
MODEL = "gpt-4o-mini" 


def intent_detection(user_input):
    messages = [
        {"role": "system", 
            "content": IntentSystemPrompt},
        {"role": "user", 
            "content": user_input}
    ]

    response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0
        )
    return response.choices[0].message.content


def goal_setting(chat_input: ChatInput, existing_goals:list=[]):
    history = chat_input.history
    if len(history) == 0:
        history.append({
            'role': 'system',
            'content': GoalSettingSystemPrompt
        })
        history.append({
            'role': 'assistant',
            'content': coachName2assistantPrompt[chat_input.coach_name]
        })

    history.append({"role": "user", "content": chat_input.user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            response_format=Goal,
            max_tokens=500,
            temperature=0
        )
        answer = response.choices[0].message.content
        print(answer)
        print(response)
        history.append({"role": "assistant", "content": answer})
        return answer, history
        
    except Exception as e:
        return e


def planning(goals: List[Goal]):
    pass 
def goal_editing(user_input, goal:Goal):
    pass 

def task_editing():
    pass

def personal_growth():
    pass 

def emotional_support():
    pass 

def other_chat():
    pass 

Intent2Func = {

}
if __name__ == '__main__': 
    print(intent_detection("hello"))    
    print(intent_detection("good morning"))
    print(intent_detection("I want to set a goal"))
    print(intent_detection("I want to learn to code"))
    print(intent_detection("I want to switch my career to become a software engineer in 3 months"))
    print(intent_detection("I feel depressed because I cannot complete my tasks in time"))