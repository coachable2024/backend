import os
import json
from typing import List, Optional, Any
from datetime import date

import uvicorn
import openai
import instructor
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from metadata import TaskExample, GoalExample, PlanExample
from src.schemas.goal.goal_models import Goal
from src.services.goal_agent.goal_setting_agent import WorkFlowManager

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
    goal: Optional[Goal]


# # Add this date serializer class
# class DateEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, date):
#             return obj.isoformat()
#         if isinstance(obj, TaskStatus):
#             return obj.value
#         if isinstance(obj, GoalStatus):
#             return obj.value
#         if isinstance(obj, GoalCategory):
#             return obj.value
#         return super().default(obj)

@app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
async def generate_answer(request_body: ChatInput):
    user_input = request_body.user_input
    user_id = 'test123'
    current_date = date.today()
    # Get data from Redis
    workflow_data_dict = await redis_client.get(user_id)
    print("\n =========== Workflow_data STARTING STATUS ===========")
    print(workflow_data_dict)
    
    # Initialize workflow_data
    workflow_data = WorkFlowManager()
    
    # Only try to parse JSON if we got data from Redis
    if workflow_data_dict is not None:
        # try:
        workflow_data_dict = json.loads(workflow_data_dict)
        workflow_data = WorkFlowManager(**workflow_data_dict)
        # except json.JSONDecodeError:
            # Handle invalid JSON data
    
    # Set basic properties
    workflow_data.goal.user_id = user_id
    workflow_data.goal.id = 'goal1'
    workflow_data.goal.created_at = date.today().strftime("%Y-%m-%d")
    
    # tag the goal and tasks in the response
    if len(workflow_data.chat_history):
        last_asked_ai_question = workflow_data.chat_history[-1]
    else:
        last_asked_ai_question = 'just started'
    
## - Only tag when input is specific
    tagging_prompt = """
   
    
        # Tagging Agent Role
        Tag user input in pydantic model **Goal** based on conversation and planning expertise.

        # Tagging Rules
        - Skip ambiguous information
        - Never tag None values
        - Only tag when the information is specific and actionable
        - Tag **clear_chat** as True if requested. Only do so when user input exactly "CLEAR CHAT" in UPPER CASE

        # Context
        Review before tagging:
        - Chat history: {chat_history}
        - Last AI question: {last_asked_ai_question}
        - Current workflow step

        # Workflow and Tagging Steps

        1. **Goal Information**
        - Do not directly ask user to provide title and description
        - Tag on input:
        - goal_title
        - goal_description

        2. **Timeline**
        - Tag: goal_target_date

        3. **Time Commitment**
        - Tag: hours_dedicated

        4. **Goal Confirmation**
        - Reference 
        - No tagging - verification step
        - Propose a general timeline that the user can follow
        
        5. **Habits**
        - Tag for each habit:
        - title
        - description
        - preferred_time ('%H:%M' format)
        - duration

        6. **Habit Confirmation**
        - No tagging - verification step

        7. **Task Planning**
        - Do research on the goal
        - Breakdown the goal to actionable tasks
        - Give at least 7 tasks 
        - Create a concrete timeline from start date {current_date} and target end date. 
        - Generate actionable task lists. Reference the structure of {TaskExample}
        - Output should have concrete time and duration {hours} of each tasks
        - Output should avoid any conflicts with habits in {habits}.
        - Create Task Objects and tag each Task field. Particularly the dates, task duration (in mintues) and start time (like "8:00 AM" )
        
        8. **Task Confirmation**
        - Confirm with user if the task breakdown looks good
        
        
            """.format(chat_history = workflow_data.chat_history,
                       last_asked_ai_question = last_asked_ai_question,
                       habits = workflow_data.goal.habits,
                       hours = workflow_data.goal.hours_dedicated,
                       current_date = current_date,
                       TaskExample = TaskExample,
                       GoalExample = GoalExample,
                       PlanExample = PlanExample,)
    response = instructor_client.chat.completions.create(
                            model=MODEL,
                            response_model=Goal,
                            messages=[{"role": "system", 
                                        "content": tagging_prompt },
                                    {"role": "user", "content": user_input}],
                            temperature=0.7
                            ) 
    
    # Convert to JSON string with custom encoder
    tagged_goal = response.dict()

    print('\n =========== answerjson =========== ', flush = True)
    print(tagged_goal)

    tasks = tagged_goal.get('tasks')
    habits = tagged_goal.get('habits')
    clear_chat = tagged_goal.get('clear_chat')
    if clear_chat:
        workflow_data = WorkFlowManager()
        await redis_client.set(user_id, json.dumps(workflow_data.dict()))
        return AnswerWithHistory(answer='cleared', history=[], goal=None)
   
    for key, value in tagged_goal.items():
        if value is not None:
            if key not in  ['tasks', 'habits']:
                try:
                    setattr(workflow_data.goal, key, value)
                except:
                    pass
    
    if tasks and len(tasks):
        for temp_task in tasks:
            print('\n =========== temp task ===========')
            print(temp_task)
            try:
                workflow_data.goal.tasks.append(Task(**temp_task))
            except:
                pass
    
    if habits and len(habits):
        for temp_habit in habits:
            print("\n ===========temp habits===========")
            print(temp_habit)
            try:
                workflow_data.goal.habits.append(Habit(**temp_habit))  
            except:
                pass     

    print('\n =========== workflow data after tagging===========')
    print(workflow_data.goal)
    # try:
    goal_dict_data = workflow_data.goal.dict()
    fields_values_to_gather = []
    for key, value in goal_dict_data.items():
        if key not in ['id','user_id' ,'status', 'created_at', 'completed_date', 'progress']:
            if value is None:
                fields_values_to_gather.append(key)

    print("\n =========== fields to gather ===========")
    print(fields_values_to_gather)
    key = fields_values_to_gather[0]
    if key in ['title', 'description']:
        information_to_gather = 'Tell me more about your goals.'
    elif key in ['target_date']:
        information_to_gather = "Ok we will start to work towards to this goal today, let's dicuss when do we want to achieve this goal, please provide a datetime."
    elif key in ['hours_dedicated']:
        information_to_gather = "How many hours do you want to dedicate to this goal every day?"
    # elif key in ['confirm_goal']:
    #     information_to_gather = "Let's review our goal and confirm the goal description, due date, and dedicated time."
    elif key in ['confirm_goal']:
        information_to_gather = "Let me know if the goal looks good to you."
    elif key  == 'add_habits':
        information_to_gather = "Do you want to add any daily routines or habits? This will help us plan the tasks regarding to the goal for you."
    # elif key == 'habits':
        # information_to_gather = "Let's plan the habits. Can you provide the habit title and description? What is the preferred time you want to do this habit daily,  and ask them about how long do they want to do this habit daily."
    elif key == 'habits':
        information_to_gather = "To avoid schedule conflicts - do you have daily routines?"
    elif key == "confirm_tasks":
        information_to_gather = "Does this schedule look good to you?"        
    else:
        information_to_gather = "The goal has been set, if you need other help, let me know!"

    print("\n=========== information_to_gather ===========")
    print(information_to_gather)
    # ai response


    system_prompt = """

            # Life Coach Agent Role
            You are an empathetic life coach helping clients set goals, plan tasks, and create schedules that work with their daily routines.

            # Context
            Review before responding:
            - Information needed: {information_to_gather}
            - Chat history: {chat_history}
            - Current workflow step

            # Goal-Setting Workflow

            1. **Goal Definition**
            - Get and clarify goal
            - Capture title and description
            - Do not directly ask user to provide "a title and a brief description"

            2. **Timeline**
            - Get target completion date

            3. **Time Commitment**
            - Get hours dedicated to goal

             4. **Goal Confirmation**
            - Reference 
            - No tagging - verification step
            - Propose a general timeline that the user can follow
            
            5. Propose a general timeline that the user can follow

            6. **Daily Routines**
            - Get habits:
            - Title/description
            - Time ('%H:%M' format)
            - Duration
            - No assumptions allowed

            7. **Habit Confirmation**
            - Verify all habit details

            8. **Task Planning**
            - Do research on the goal
            - Breakdown the goal to actionable tasks
            - Give at least 7 tasks 
            - Create a concrete timeline from start date ({current_date}) and target end date. Refernce the structure of {PlanExample}
            - Generate actionable task lists. Reference the structure of {TaskExample}
            - Output should have concrete time and duration {hours} of each tasks
            - Output should avoid any conflicts with habits in {habits}.
            - Create Task Objects and tag each Task field. Particularly the dates, task duration (in mintues) and start time (like "8:00 AM" )

            9. **Task Confirmation**
            - Confirm with user if the task breakdown looks good
            
            # Response Rules
            1. Be succinct. Address emotional needs first
            2. Present tasks when {tasks} is non-empty
            3. One simple question at a time
            4. Stay on current workflow step
            5. No assumed values

"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", 
                "content": system_prompt.format(
                            information_to_gather = information_to_gather, 
                                                chat_history = workflow_data.chat_history,
                                                habits = workflow_data.goal.habits,
                                                tasks = workflow_data.goal.tasks,
                                                hours = workflow_data.goal.hours_dedicated,
                                                current_date = current_date,
                                                GoalExample = GoalExample,
                                                TaskExample = TaskExample,
                                                PlanExample = PlanExample,
                                                )},
            {"role": "user", "content": user_input}],
        max_tokens=4000,
        temperature=0.7
    )
    answer = response.choices[0].message.content
    workflow_data.chat_history.append({'role': 'user', 
                                    'content': user_input})
    # append to chat history
    workflow_data.chat_history.append({'role': 'assistant', 
                                    'content': answer})
    
    # save data to redis
    print("\n ========= workflow data =========")
    print(workflow_data.dict())
    await redis_client.set(user_id, json.dumps(workflow_data.dict()))
    print(workflow_data)

    print('\n ========= give answer to the user ============')
    print(answer)
    return AnswerWithHistory(answer=answer, history=workflow_data.chat_history, goal=workflow_data.goal)

    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000) 

