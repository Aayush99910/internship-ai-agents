from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pandas as pd
import heapq
from model_functions import predict_priority
from task_functions import load_data, map_importance_to_number

# App setup
app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset and initialize heap
data = load_data()
task_heap = []

def rebuild_heap():
    global task_heap
    task_heap = []
    heapq.heapify(task_heap)
    for _, row in data.iterrows():
        priority = map_importance_to_number(row["Importance"])
        heapq.heappush(task_heap, (pd.to_datetime(row["Deadline"]), -1 * priority, row.to_dict()))

rebuild_heap()

# Pydantic model
class Task(BaseModel):
    taskName: str
    deadline: str
    estimation: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
    importance: Optional[str] = None

class PredictInput(BaseModel):
    deadline: str
    dateCreated: str
    estimation: Optional[float] = None

# Routes
@app.get("/api/tasks")
def get_all_tasks():
    sorted_heap = sorted(task_heap)
    tasks = [task for _, _, task in sorted_heap]
    return tasks

@app.get("/api/most_important")
def get_most_important():
    if task_heap:
        _, _, task = task_heap[0]
        return task
    return {"message": "No tasks in your list."}

@app.post("/api/tasks")
def add_task(task: Task):
    global data
    deadline = pd.to_datetime(task.deadline)
    created_at = datetime.now()

    # Predict priority if not provided
    predicted_importance = predict_priority(deadline, created_at, task.estimation)
    importance = task.importance or predicted_importance

    new_task = {
        "Task Name": task.taskName,
        "Deadline": deadline,
        "Importance": importance,
        "Description": task.description,
        "Date Created": created_at,
        "Estimation Time": task.estimation,
        "Status": task.status
    }

    data.loc[len(data)] = new_task #type:ignore 
    priority = map_importance_to_number(importance)
    heapq.heappush(task_heap, (deadline, -1 * priority, new_task))

    data.to_csv("dataset/sample_task_dataset.csv", index=False)
    return {"message": "Task added successfully!", "task": new_task}

@app.post("/api/predict_priority")
def predict_task_priority(input1: PredictInput):
    try:
        deadline = pd.to_datetime(input1.deadline, utc=True)
        date_created = pd.to_datetime(input1.dateCreated, utc=True)
        priority = predict_priority(deadline, date_created, input1.estimation)
        return {"priority": priority}
    except Exception as e:
        return {"error": f"Failed to predict priority: {str(e)}"}


@app.post("/api/save")
def save_and_exit():
    data.to_csv("dataset/sample_task_dataset.csv", index=False)
    return {"message": "Tasks saved successfully!"}