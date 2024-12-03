import os
import json

import openai
import instructor
import duckdb
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from metadata import coachName2startingHistory
from data_model import ChatInput, AnswerWithHistory, Task, Goal

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
            You are helping a user: {user_id} set a goal and create tasks to achieve it. 
            Tag the goal and tasks you create for this user in the response. Tasks cannot be an empty list.
            """.format(user_id=user_id)},
            {"role": "user", "content": user_input}],
)       
    # Convert to JSON string with custom encoder
    answer_json = json.loads(response.model_dump_json())
   
    with open("goal_temp.json", "w") as json_file:
        json.dump(answer_json, json_file, indent=4)
    with open("task_temp.json", "w") as json_file:
        json.dump(answer_json['tasks'], json_file, indent=4)
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
                    """.format(user_input=user_input, goal_result=answer_json, task_result=answer_json['tasks'])})
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



## TODO: integrate with frontend and test 
@app.post("/goal_setting_chat/", response_model=AnswerWithHistory)
async def goal_setting_chat(request_body: ChatInput):
    history = request_body.history.copy()
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