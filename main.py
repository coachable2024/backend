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
    description: str = Field(description="The description of the task")
    start_date: date = Field(description="The start date of the task")
    end_date: date = Field(description="The end date of the task")
    status: TaskStatus = Field(description="The status of the task")

class Goal(BaseModel):
    description: str
    start_date: date = Field(description="The start date of the goal")
    end_date: date = Field(description="The end date of the goal")
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


@app.post("/generate-answer-structured-output/", response_model=Answer)
async def generate_answer(question_data: Question):
    try:
        response = instructor_client.chat.completions.create(
        model=MODEL,
        response_model=Goal,
        messages=[{"role": "user", "content": question_data.question}],
    )       
        # Convert to JSON string with custom encoder
        answer_json = json.dumps(response.dict(), cls=DateEncoder)
        
        return Answer(answer=answer_json)
    
    except openai.APIError as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


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