import os
import json
from typing import List, Optional, Any, Dict
from enum import Enum
from datetime import date
import pandas as pd

import openai
import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from metadata import coachName2startingHistory

import duckdb

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key="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")
instructor_client = instructor.from_openai(client)
MODEL = "gpt-4o" # or any other available model

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

# Configure Redis connection parameters
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    decode_responses=True  # Automatically decode responses to strings
)



steps = [
    "Step 1: communicate with the client about what their goal is and clarify as needed",
    "Step 2: discuss with the client their timeframe to achieve the goal",
    "Step 3: check whether the client has any habit routine or self-care demand they need to consider when working on the goal",
    "Step 4: break down the goal into concrete and actionable tasks",
    "Step 5: take into consideration other goals if any, habits and self-care demands, and arrange the clients' calendar by assigning the starting and ending date times for each task",
]


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

class GoalCategory(Enum):
    HABIT = "Habit"
    PROJECT = "Project"

class GoalStatus(Enum):
    ACTIVE = "Active"
    COMPLETED = "Completed"
    INACTIVE = "Inactive"

class Task(BaseModel):
    id: Optional[str] = Field(default=None, description="The id of the task")
    title: Optional[str] = Field(default=None, description="The title of the task")
    description: Optional[str] = Field(default=None, description="The description of the task")
    status: Optional[TaskStatus] = Field(default=None, description="The status of the task")
    priority: Optional[str] = Field(default=None, description="The priority of the task")
    # updated_at: str = Field(description="The date the task was last updated")
    # created_at: str = Field(description="The date the task was created")
    due_date: Optional[str] = Field(default=None, description="The due date of the task")
    start_date_time: Optional[str] = Field(default=None, description="The start date time of the task")
    # end_date_time: str = Field(description="The end date time of the task")
    duration: Optional[str] = Field(default=None, description="The interval of the task")

class Goal(BaseModel):
    id: Optional[str] = Field(default=None, description="The id of the goal")
    user_id: Optional[str] = Field(default=None, description="The user id of the user who set the goal")
    # category: GoalCategory = Field(description="The category of the goal")
    title: Optional[str] = Field(default=None, description="The title of the goal")
    description: Optional[str] = Field(default=None, description="The description of the goal")
    reward: Optional[str] = Field(default=None, description="The reward of the goal")
    motivation: Optional[str] = Field(default=None, description="The motivation of the goal")
    target_date: Optional[str] = Field(default=None, description="The target date of the goal")
    confirmed: Optional[bool] = Field(default=None, description="Whether the goal is confirmed")
    tasks: Optional[List[Task]] = Field(default=[], description="The tasks associated with the goal")
    # the rest will be tagged by user or constant
    status: Optional[str] = Field(default=GoalStatus.ACTIVE.value, description="The status of the goal")
    created_at: Optional[str] = Field(default=None, description="The start date of the goal")
    completed_date: Optional[str] = Field(default=None, description="The end date of the goal")
    # updated_at: str = Field(description="The end date of the goal")
    progress: Optional[float] = Field(default=None, description="The percentage progress of the goal")
    

class WorkFlowManager(BaseModel):
    goal: Goal = Goal()
    chat_history: List[Any] = []


# Add this date serializer class
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, TaskStatus):
            return obj.value
        if isinstance(obj, GoalStatus):
            return obj.value
        if isinstance(obj, GoalCategory):
            return obj.value
        return super().default(obj)

@app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
async def generate_answer(request_body: ChatInput):
    user_input = request_body.user_input
    #Hello, I'd like to set a goal to finish reading my coding book, start from dec, 10, 2024, end at jan, 10, 2025
    user_id = 'test123'
    workflow_data_dict = await redis_client.get(user_id)
    workflow_data_dict = json.loads(workflow_data_dict)
    print("---saved data---")
    print(workflow_data_dict)
    workflow_data = WorkFlowManager()
    if workflow_data_dict is None:
        workflow_data = WorkFlowManager()
    else:
        workflow_data = WorkFlowManager(**workflow_data_dict)
    workflow_data.goal.user_id = user_id
    workflow_data.goal.id = 'goal1'
    workflow_data.goal.created_at = date.today().strftime("%Y-%m-%d")
    # tag the goal and tasks in the response
    response = instructor_client.chat.completions.create(
    model=MODEL,
    response_model=Goal,
    messages=[{"role": "system", 
                "content": """
                You are a life coach helping the client to set a goal and break it down to tasks to achieve the goal. 
                Your task is to tag information in pydantic model Goal based on user input.
                Only tag the field when user input is clear. Do not tag the field when user input is ambiguous, and you cannot determine the value.
                Do not tag None values to any fields. 
                Please follow the steps below
            Step 1: communicate with the client about what their goal is and clarify as needed. Tag the goal title and description in this step.
            Step 2: discuss with the client the reward and motivation of the goal.
            Step 3: discuss with the client their timeframe to achieve the goal. Tag the goal target date in this step.
            Step 4: After user confirm the goal they want to set, it is your task to break down the goal into concrete and actionable tasks. Tag the tasks in this step, it cannot be an empty list.
            Tag the goal and tasks you create for this user in the response. Tasks cannot be an empty list.
            """},
            {"role": "user", "content": user_input}],
) 

    # Convert to JSON string with custom encoder
    tagged_goal = response.dict()
    print('----answerjson----')
    print(tagged_goal)
    tasks = tagged_goal['tasks']
    for key, value in tagged_goal.items():
        if value:
            setattr(workflow_data.goal, key, value)
    print('----here----')
    try:
        goal_dict_data = workflow_data.goal.dict()
        fields_values_to_gather = []
        for key, value in goal_dict_data.items():
            if key not in ['status', 'created_at', 'completed_date', 'progress']:
                if value is None:
                    fields_values_to_gather.append(key)


        if key in ['title', 'description']:
            information_to_gather = 'Please provide the title and describe your goal.'
        elif key in ['reward', 'motivation']:
            information_to_gather = "let's think about your motivations of setting this goal, and set rewards for this goal."
        elif key in ['target_date']:
            information_to_gather = "Ok we will start to work towards to this goal today, let's dicuss when do we want to achieve this goal, please provide a datetime."
        elif key in ['confirmed']:
            information_to_gather = "Let's review our goal and task and confirm them"
        else:
            information_to_gather = "The goal has been set, if you need other help, let me know!"

        # ai response
        system_prompt = """
                    You are a life coach helping the client to set a goal and break it down to tasks to achieve the goal. 
                    Your task is to guide users to set and confirm the goal that they want to set, and break them down to tasks.
                    You are provided with {chat_history}, review the chat history, identify which steps in the goal setting workflow are we: 
                    Only gather information for one step in one response, otherwise users maybe overwhelmed.
                Step 1: communicate with the client about what their goal is and clarify as needed. Tag the goal title and description in this step.
                Step 2: discuss with the client the reward and motivation of the goal.
                Step 3: discuss with the client their timeframe to achieve the goal. Tag the goal target date in this step.
                Step 4: break down the goal into concrete and actionable tasks. 
                This is the information we need to gather in this response, only ask questions related to this:
                {information_to_gather}
                Additionally, whenever users have issues understanding goal or tasks, or need emotional support, tackle those first, them gracefully guide them to the goal setting workflow.

    """
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", 
                    "content": system_prompt.format(information_to_gather = information_to_gather, chat_history=workflow_data.chat_history)},
                {"role": "user", "content": user_input}],
            max_tokens=500,
            temperature=0.7
        )
        answer = response.choices[0].message.content
        workflow_data.chat_history.append({'role': 'user', 
                                        'content': user_input})
        # append to chat history
        workflow_data.chat_history.append({'role': 'assistant', 
                                       'content': answer})
         # save data to redis
        await redis_client.set(user_id, json.dumps(workflow_data.dict()))
    except Exception as e:
        print(str(e))
        answer = 'wrong'
    print('all goood now')
    print(workflow_data.chat_history)
    print(answer)
    # try:
    return AnswerWithHistory(answer=answer, history=workflow_data.chat_history)
    # except openai.APIError as e:
    #     raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


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

@app.get("/get_goal/")
async def get_goal():
    user_id = "123"
    # goal_result = duckdb.sql("SELECT * FROM 'goal_temp.json' where user_id == {}".format(user_id))
    # task_result = duckdb.sql("SELECT * FROM 'task_temp.json' where user_id == {}".format(user_id))
    # add data to duckdb
    conn = duckdb.connect()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks AS
    SELECT * FROM read_json_auto(?)
    """, ['task_temp.json'])
    
    # Verify data loaded
    df = conn.execute("SELECT * FROM tasks").fetchdf()
    print("Existing Data:")
    print(df)
    # temp_goals = pd.read_json("goal_temp.json", lines=True)
    temp_tasks = pd.read_json("task_temp.json")
    print(temp_tasks)
    print("temp_tasks:")
    print(temp_tasks.values.tolist())
    conn.execute("""
        INSERT INTO tasks (id, title, description, status, updated_at, created_at, priority, start_date, due_date, start_time, end_time, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, temp_tasks.values.tolist())

    print("New users inserted successfully.")

    df_updated = conn.execute("SELECT * FROM tasks").fetchdf()
    print(df_updated)
    return df_updated

# ## TODO: integrate with frontend and test 
# @app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
# async def goal_setting_chat(request_body: ChatInput):
#     history = request_body.history
#     if len(history) == 0:
#         history = coachName2startingHistory[request_body.coach_name]
    
#     # user has changed coach, reset the system prompt and append it to history
#     if history[0] != coachName2startingHistory[request_body.coach_name][0]:
#         history.append(coachName2startingHistory[request_body.coach_name][0])

#     history.append({"role": "user", "content": request_body.user_input})
    
#     try:
#         response = client.chat.completions.create(
#             model=MODEL,
#             messages=history,
#             max_tokens=500,
#             temperature=0.7
#         )

#         answer = response.choices[0].message.content
#         history.append({"role": "assistant", "content": answer})
        
#         return AnswerWithHistory(answer=answer, history=history)
    
#     except openai.APIError as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 