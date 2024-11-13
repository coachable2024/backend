# Question Answering API

## Useful Links and Information for collaborative development
[PRD (Google Doc, need permission)](https://docs.google.com/document/d/1KzqLgfS0sRDiNkEFHSO3HUFSKJ3iLQN0CHAPmWf_-HU/edit?tab=t.0)

Hackathon signup and contact info
- team name: coachable 
- email:coachable666@gmail.com

## Description
A FastAPI-based backend API supporting the frontend of [the coachable app](https://coachable-webapp.vercel.app/).

## Setup

1. Create a virtual environment
```
python -m venv .venv
```

2. Install dependencies
```
pip install -r requirements.txt
```
Also, make sure to set up the environment variables in the `.env` file， including
```
OPENAI_API_KEY=<your openai api key>
```

3. Run the server
```
python main.py
```
