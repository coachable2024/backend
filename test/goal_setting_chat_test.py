## temporary test file, will be replaced by pytest with mock data

import requests

url = "http://localhost:8000/goal_setting_chat/"

## TODO: to enrich and move to test data
user_inputs = [
    "I want to learn to code",
    "I want to be able to write a web app for my amazon store. I've never done any coding",
    "Can you make a day-to-day learning plan for me?",
    "Thank you"
]

if __name__ == "__main__":
    history = []
    for user_input in user_inputs:
        response = requests.post(url, json={
            'user_input':user_input,
            "coach_name": 'Luna',
            "history": history
        } )
        assert response.status_code == 200
        output = response.json()
        answer = output["answer"]
        history = output["history"]
    assert answer is not None
    assert isinstance(history, list)
    assert len(history) == 10  # 2 + 4 * 2
    assert history[-1]['role'] == 'assistant'