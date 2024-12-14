# Question Answering API

## Useful Links and Information for collaborative development
[PRD (Google Doc, need permission)](https://docs.google.com/document/d/1KzqLgfS0sRDiNkEFHSO3HUFSKJ3iLQN0CHAPmWf_-HU/edit?tab=t.0)
[API Contract](https://docs.google.com/document/d/1AjE7zVeTn9MzTyXQhw9iUfGOrFbEwwQAGwWcApp7s-g/edit?tab=t.0)

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
Also, make sure to set up the environment variables in the `.env` file，including
```
OPENAI_API_KEY=<your openai api key>
```
3. Set up redis
```
brew update

brew install redis

redis-server --version 

brew services start redis

redis-cli ping, you should be able to see PONG

if you need to stop redis:
brew services stop redis
```
3. Run the server
```
python main.py
```

4. The API will be hosted at `http://localhost:8000/docs`.
