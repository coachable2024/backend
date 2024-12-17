from datetime import datetime, timedelta
from typing import List

def generate_dates(start_date: datetime, num_days: int, hour: int, minute: int) -> List[datetime]:
    return [
        start_date.replace(hour=hour, minute=minute) + timedelta(days=i)
        for i in range(num_days)
    ]

GOAL_EXAMPLES = [
    {
        "id": "1",
        "title": "Complete Project Milestone",
        "description": "Deliver key features to customers",
        "category": "career",
        "relatedTasks": ["1"],
        "targetDate": datetime(2024, 6, 30),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "startDate": datetime.now(),
        "completedDate": datetime.now(),
        "SettingStatus": "draft"
    },
    {
        "id": "2",
        "title": "Improve Fitness Level",
        "description": "Better health and energy",
        "category": "health",
        "relatedTasks": ["2"],
        "targetDate": datetime(2024, 12, 31),
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "startDate": datetime.now(),
        "completedDate": datetime.now(),
        "SettingStatus": "draft"
    }
]



HABIT_EXAMPLES = [
    {
        "id": "1",
        "title": "Morning Meditation",
        "description": "Start the day with mindfulness",
        "schedule": {
            "frequency": "daily",
            "timesPerPeriod": 1,
            "defaultDuration": 15,
            "preferredTime": datetime.now().replace(hour=7, minute=0),
            "timeSlots": [],
            "weeklySchedules": []
        },
        "status": "active",
        "createdAt": datetime.now() - timedelta(days=30),
        "updatedAt": datetime.now(),
        "startDate": datetime.now() - timedelta(days=30),
        "scheduledDates": generate_dates(
            datetime.now() - timedelta(days=30),
            60,
            7,
            0
        ),
        "completedDates": generate_dates(
            datetime.now() - timedelta(days=15),
            15,
            7,
            0
        )
    },
    {
        "id": "2",
        "title": "Evening Workout",
        "description": "Strength training and cardio",
        "schedule": {
            "frequency": "weekly",
            "timesPerPeriod": 3,
            "defaultDuration": 45,
            "preferredTime": datetime.now().replace(hour=18, minute=30),
            "timeSlots": [],
            "weeklySchedules": [{
                "weekStartDate": (datetime.now() - timedelta(days=datetime.now().weekday())),
                "plannedDays": [1, 3, 5]  # Monday, Wednesday, Friday
            }]
        },
        "status": "active",
        "createdAt": datetime.now() - timedelta(days=14),
        "updatedAt": datetime.now(),
        "startDate": datetime.now() - timedelta(days=14),
        "scheduledDates": [
            datetime.now() - timedelta(weeks=i, days=d)
            for i in range(6)
            for d in [0, 2, 4]  # Monday, Wednesday, Friday
        ]
    },
    {
        "id": "3",
        "title": "Reading",
        "description": "Read a book for personal growth",
        "schedule": {
            "frequency": "daily",
            "timesPerPeriod": 1,
            "defaultDuration": 30,
            "preferredTime": datetime.now().replace(hour=21, minute=0),
            "timeSlots": [],
            "weeklySchedules": []
        },
        "status": "active",
        "createdAt": datetime.now() - timedelta(days=7),
        "updatedAt": datetime.now(),
        "startDate": datetime.now() - timedelta(days=7),
        "scheduledDates": generate_dates(
            datetime.now() - timedelta(days=7),
            7,
            21,
            0
        )
    },
    {
        "id": "4",
        "title": "Weekly Planning",
        "description": "Plan the week ahead",
        "schedule": {
            "frequency": "weekly",
            "timesPerPeriod": 1,
            "defaultDuration": 60,
            "preferredTime": datetime.now().replace(hour=10, minute=0),
            "timeSlots": [],
            "weeklySchedules": [{
                "weekStartDate": (datetime.now() - timedelta(days=datetime.now().weekday())),
                "plannedDays": [0]  # Sunday
            }]
        },
        "status": "active",
        "createdAt": datetime.now() - timedelta(days=21),
        "updatedAt": datetime.now(),
        "startDate": datetime.now() - timedelta(days=21),
        "scheduledDates": [
            (datetime.now() - timedelta(weeks=i)).replace(hour=10, minute=0)
            for i in range(3)
        ]
    }
]

TASK_EXAMPLES = [
    {
        "id": "1",
        "title": "Set Up a Tracker for webpage design",
        "description": "",
        "status": "in-progress",
        "priority": "high",
        "duration": 120,  # 2 hours
        "startTime": datetime(2024, 12, 20, 9, 0),
        "dueDate": datetime(2024, 12, 31),
        "createdAt": datetime(2024, 3, 20),
        "updatedAt": datetime(2024, 3, 20),
        "relatedGoal": None  # Optional field from your Task type
    },
    {
        "id": "2",
        "title": "Design Page Layout",
        "description": "Create home page layout",
        "status": "in-progress",
        "priority": "medium",
        "duration": 180,  # 3 hours
        "startTime": datetime(2024, 12, 23, 13, 30),
        "dueDate": datetime(2024, 12, 23),
        "createdAt": datetime(2024, 3, 19),
        "updatedAt": datetime(2024, 3, 21),
        "relatedGoal": None
    },
    {
        "id": "3",
        "title": "Improve features",
        "description": "improve task and goal features",
        "status": "completed",
        "priority": "low",
        "duration": 90,  # 1.5 hours
        "startTime": datetime(2024, 12, 18, 15, 0),
        "dueDate": datetime(2024, 12, 28),
        "createdAt": datetime(2024, 3, 18),
        "updatedAt": datetime(2024, 3, 22),
        "relatedGoal": None
    }
]