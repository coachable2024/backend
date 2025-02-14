
goal_tagging_prompt = """    
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
            """



# Coach configurations remain the same
coachName2startingHistory = {
    'Luna': [
            {"role": "system", 
             "content": "You are Luna, a warm and understanding coach who focuses on supportive and \
                nurturing guidence, good at emotional support, work-life balance, and personal growth."},
            {"role": "assistant", 
             "content": "Hi! I'm Luna, a Empathetic Guide. I'm here to help you achieve your goals. \
                Could you tell me about the specific goal you'd like to work on?"}
    ],
    'Max': [
        {"role": "system", 
         "content": "You are Max, an analytical and data-driven coach who provides clear, structured \
            approaches to achieving goals, good at structured planning and efficiency."},
        {"role": "assistant", 
         "content": "Hi! I'm Max, a Strategic Partner. I'm here to help you achieve your goals. Could \
            you tell me about the specific goal you'd like to work on?"}
    ],
    'Zara': [
        {"role": "system", 
         "content": "You are Zara, a dynamic and action-oriented coach who brings enthusiasm and high \
        energy to coachee's goal journey, good at positive motivation."},
        {"role": "assistant", 
         "content": "Hi! I'm Zara, a Energetic Motivator. I'm here to help you achieve your goals. \
            Could you tell me about the specific goal you'd like to work on?"}
    ],
    'Sage': [
        {"role": "system", 
         "content": "You are Sage, a thoughtful coach who combines practical advice and philosophical \
            insights, good at deep reflection, holistic approach and long-term growth."},
        {"role": "assistant", 
         "content": "Hi! I'm Sage, a Wise Mentor. I'm here to help you achieve your goals. Could you \
            tell me about the specific goal you'd like to work on?"}
    ]
}

# Fixed TaskExample structure
TaskExample = {
    "tasks": [
        {
            "id": "1",
            "category": "Goal_Related_Task",
            "title": "Set Up a Tracker for webpage design",
            "description": "",
            "preferred_time": "09:00",
            "duration": 2,
            "completed_date": "2024-12-31",
            "status": "Active",
            "start_date": "2024-12-20",
            "end_date": "2024-12-31"
        },
        {
            "id": "2",
            "category": "Goal_Related_Task",
            "title": "Design Page Layout",
            "description": "Create home page layout",
            "preferred_time": "13:30",
            "duration": 3,
            "completed_date": "2024-12-31",
            "status": "Active",
            "start_date": "2024-12-23",
            "end_date": "2024-12-28"
        },
        {
            "id": "3",
            "category": "Goal_Related_Task",
            "title": "Improve features",
            "description": "improve task and goal features",
            "preferred_time": "15:00",
            "duration": 1,
            "completed_date": "2024-12-31",
            "status": "Active",
            "start_date": "2024-12-18",
            "end_date": "2024-12-28"
        }
    ]
}

# GoalExample stays the same
GoalExample = {
    "goals": [
        {
            "id": "goal-001",
            "user_id": "user-123",
            "title": "Complete Project Milestone",
            "description": "Deliver key features to customers by Q2 2024",
            "target_date": "2024-06-30",
            "hours_dedicated": 4,
            "confirm_goal": True,
            "add_habits": True,
            "habits": ["habit-001", "habit-002"],
            "confirm_habit": True,
            "tasks": ["task-001", "task-002"],
            "confirm_tasks": True,
            "status": "active",
            "created_at": "2024-01-01",
            "completed_date": None,
            "clear_chat": False
        },
        {
            "id": "goal-002",
            "user_id": "user-123",
            "title": "Improve Fitness Level",
            "description": "Achieve better health and energy through regular exercise",
            "target_date": "2024-12-31",
            "hours_dedicated": 2,
            "confirm_goal": True,
            "add_habits": True,
            "habits": ["habit-003", "habit-004"],
            "confirm_habit": True,
            "tasks": ["task-003", "task-004"],
            "confirm_tasks": True,
            "status": "active",
            "created_at": "2024-01-01",
            "completed_date": None,
            "clear_chat": False
        }
    ]
}


ResearchExample = """


"""


PlanExample = """
Stage 1: Build a foundational understanding of what Product Management entails.
Stage 2: Understand PM frameworks, tools, and methodologies.
Stage 3: Developing Customer Empathy. Learn to think from the customer’s perspective and develop empathy.
Stage 4: Leveraging Data Skills for PM. Connect your Data Science expertise to PM tasks and decision-making.
"""


other = """
Stage 1 Breakdown: Build a foundational understanding of what Product Management entails.

Day 1-3:
    Task: Read the first two chapters of Inspired by Marty Cagan (approx. 30–40 pages).
    Duration: 3 days | 2 hours every day 
    Output: Note down key takeaways about the role and responsibilities of a PM.

Day 4-7:
    Task: Research online about the differences between PM and Data Science roles.
    Duration: 4 days | 2 hours every day 
    Output: Create a short comparison chart highlighting transferable skills and gaps.

Day 8-10:

    Task: Watch a 30–60 minute YouTube video or a lecture on Product Management Fundamentals.
    Duration: 3 days | 1.5 hours every day 
    Output: Write down three key insights about what makes a good PM.

Day 11:
    Rest day

Day 12-16:

    Task: Research real-world PM job descriptions (3–5).
    Duration: 2 hours
    Output: Highlight recurring skills, tools, and requirements in a document.

Day 17-18:

    Task: Reflect on the week’s learnings and write a summary of your understanding of PM.
    Duration: 1.5 hours
    Output: Create a mind map or a brief document on “What PMs Do and Why.”

Day 19-20:
    Task: Rest or review Inspired highlights and insights from the week.
    Duration: 2 hours
    Output: Refine your notes and prepare for Week 2.


Stage 2 Breakdown: Understand PM frameworks, tools, and methodologies.
Day 21-25:
    Task: Read about Agile and Scrum methodologies (choose a blog or video tutorial).
    Duration: 2 hours
    Output: Create a basic outline of how Agile/Scrum works.

Day 26-28:
    Task: Learn about tools like Jira and Trello through short tutorials (official or YouTube).
    Duration: 2 hours
    Output: Explore Trello by creating a basic board for your daily tasks.

Day 29-30:
    Task: Study product roadmaps and OKRs through blogs or case studies.
    Duration: 2 hours
    Output: Draft a simple OKR framework for a mock project idea.

Day 31-35:
    Task: Continue exploring Scrum roles (e.g., Product Owner, Scrum Master).
    Duration: 2 hours
    Output: Summarize how these roles interact with PMs.

Day 36-38:
    Task: Start reading about prioritization frameworks (e.g., RICE, MoSCoW).
    Duration: 2 hours
    Output: Create a mock prioritization list using a framework.

Day 39-40:
    Task: Read or watch content about creating user stories.
    Duration: 2 hours
    Output: Write three sample user stories for a simple app idea.

Day 41-42
    Task: Review concepts from the week and practice creating a mini Agile board.
    Output: Build confidence in Agile and PM basics.

Day 43:
    Rest day

Stage 3 Breakdown: Developing Customer Empathy. Learn to think from the customer’s perspective and develop empathy.

Day 44:
    Task: Read about customer research methods (e.g., interviews, surveys).
    Output: Create a mock list of questions for a customer interview.

Day 45:

    Task: Study basic UX principles (e.g., user flows, wireframes).
    Output: Sketch a simple user flow for a mock app.

Day 46:

    Task: Watch a tutorial on design thinking and problem-solving.
    Output: Outline the steps of the design thinking process.

Day 47:

    Task: Read a case study of a product solving a customer problem.
    Output: Summarize the key customer pain points and how they were addressed.

Day 48:

    Task: Learn about user persona creation.
    Output: Create one user persona for your mock app.

Day 49:

    Task: Practice creating a basic user story map for your mock app.
    Output: Identify key features and their sequence.

Day 50:

    Task: Review the week’s learnings and refine your customer personas or user story map.
    Output: Develop a stronger customer-first mindset.

Stage 4 Breakdown: Leveraging Data Skills for PM. Connect your Data Science expertise to PM tasks and decision-making.

Day 51:

    Task: Research how PMs use data for decision-making.
    Output: Write down 3–5 examples of data-driven PM decisions.

Day 52:

    Task: Learn about product metrics (e.g., DAU, MAU, retention rate).
    Output: Define 3 key metrics for your mock app.

Day 53:

    Task: Explore storytelling with data (e.g., videos or blogs).
    Output: Create a short mock data presentation in PowerPoint or Google Slides.

Day 54:

    Task: Research A/B testing for PMs.
    Output: Design a mock A/B test for a feature in your app.

Day 55:

    Task: Practice communicating insights from a dataset you’ve worked on previously.
    Output: Frame the insights in a business context (focus on outcomes and recommendations).

Day 56:

    Task: Review your current skill set and identify gaps.
    Output: Write a short plan for bridging those gaps in the next two months.

Day 57:

    Task: Summarize the month’s learnings in a document or presentation.
    Output: Create a one-page “Product Management Foundations” summary.
"""