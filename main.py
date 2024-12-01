import os
import json
from typing import List
from enum import Enum
from datetime import date

import openai
import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from metadata import coachName2startingHistory

import redis
import duckdb

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
rd = redis.Redis(connection_pool=pool)
# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key="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")
instructor_client = instructor.from_openai(client)
MODEL = "gpt-4o-mini" # or any other available model

app = FastAPI(
    title="Coachable API",
    description="Backend API for Coachable APP",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    question: str

class Answer(BaseModel):
    answer: str | dict

class HistoryRecord(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    user_input: str
    coach_name: str
    history: List[HistoryRecord] = Field(default_factory=list)

class AnswerWithHistory(BaseModel):
    answer: str
    history: List[HistoryRecord]

class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"

class Task(BaseModel):
    id: str = Field(description="The id of the task")
    title: str = Field(description="The title of the task")
    description: str = Field(description="The description of the task")
    status: TaskStatus = Field(description="The status of the task")
    updated_at: str = Field(description="The date the task was last updated")
    created_at: str = Field(description="The date the task was created")
    priority: str = Field(description="The priority of the task")
    due_date: str = Field(description="The due date of the task")

class Goal(BaseModel):
    user_id: str = Field(description="The user id of the goal")
    description: str
    start_date: str = Field(description="The start date of the goal")
    end_date: str = Field(description="The end date of the goal")
    tasks: List[Task] = Field(description="The tasks associated with the goal")

# Add this date serializer class
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        return super().default(obj)

## Sample endpoint for reference, not used in the app, will be removed 
@app.post("/generate-answer/", response_model=Answer)
async def generate_answer(question_data: Question):
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,  
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question_data.question}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        # Extract the generated answer
        answer = response.choices[0].message.content
        
        return Answer(answer=answer)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/generate-answer-structured-output/", response_model=AnswerWithHistory)
async def generate_answer(request_body: ChatInput):
    user_input = request_body.user_input
    #Hello, I'd like to set a goal to finish reading my coding book, start from dec, 10, 2024, end at jan, 10, 2025
    user_id = '123'
    response = instructor_client.chat.completions.create(
    model=MODEL,
    response_model=Goal,
    messages=[{"role": "system", 
                "content": """You are Luna, a warm and understanding coach who focuses on supportive and \
            nurturing guidence, good at emotional support, work-life balance, and personal growth.
            You are helping a user: {user_id} set a goal and create tasks to achieve it. Tag the information users provided.
            When you tag Enum values, use the value, not the enum.
            """.format(user_id=user_id)},
            {"role": "user", "content": user_input}],
)       
    # Convert to JSON string with custom encoder
    answer_json = response.dict()
    for task in answer_json['tasks']:
        task['status'] = task['status'].value
    print(answer_json)
    with open("goal.json", "w") as json_file:
        json.dump(answer_json, json_file, indent=4)
    with open("task.json", "w") as json_file:
        json.dump(answer_json['tasks'], json_file, indent=4)
    user_id = "123"
    goal_result = duckdb.sql("SELECT * FROM 'goal.json'")
    task_result = duckdb.sql("SELECT * FROM 'task.json'")
    print(goal_result)
    print(task_result)

    # response to user
    history = request_body.history
    if len(history) == 0:
        history = coachName2startingHistory[request_body.coach_name]
    
    # user has changed coach, reset the system prompt and append it to history
    if history[0] != coachName2startingHistory[request_body.coach_name][0]:
        history.append(coachName2startingHistory[request_body.coach_name][0])

    history.append({"role": "system", "content": """
                    You are Luna, a warm and understanding coach who focuses on supportive and \
                    nurturing guidence, good at emotional support, work-life balance, and personal growth.
                    Here is the user input: {user_input}
                    Here is the goal you set for the user: {goal_result}
                    Here are the tasks you created for the user: {task_result}
                    Ask user if they would like to add, remove or edit any tasks.
                    """.format(user_input=user_input, goal_result=goal_result, task_result=task_result)})
    history.append({"role": "user", "content": request_body.user_input})
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            max_tokens=500,
            temperature=0.7
        )

        answer = response.choices[0].message.content
        print(answer)
        history.append({"role": "assistant", "content": answer})
        
        return AnswerWithHistory(answer=answer, history=history)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/get_goal/")
async def get_goal(request_body: ChatInput):
    user_id = request_body.user_id
    result = duckdb.sql("SELECT * FROM 'example.json' where user_id == {}".format(user_id))
    return result

## TODO: integrate with frontend and test 
@app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
async def goal_setting_chat(request_body: ChatInput):
    history = request_body.history
    if len(history) == 0:
        history = coachName2startingHistory[request_body.coach_name]
    
    # user has changed coach, reset the system prompt and append it to history
    if history[0] != coachName2startingHistory[request_body.coach_name][0]:
        history.append(coachName2startingHistory[request_body.coach_name][0])

    history.append({"role": "user", "content": request_body.user_input})
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=history,
            max_tokens=500,
            temperature=0.7
        )

        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        
        return AnswerWithHistory(answer=answer, history=history)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 