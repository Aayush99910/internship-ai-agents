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

# Pydantic model for task 
class Task(BaseModel):
    taskName: str
    deadline: str 
    estimation: Optional[float] = None 
    description: Optional[str] = None 
    status: Optional[str] = None 
    importance: Optional[str] = None 

# need to write same thing for input that needs to be predicted
class PredictInput(BaseModel):
    deadline: str 
    dateCreated: str 
    estimation: Optional[float] = None 

# writing routes (APIs)
# this is for all tasks
@app.get("/api/tasks")
def get_all_tasks():
    sorted_heap = sorted(task_heap)
    tasks = [task for _, _, task in sorted_heap]
    return tasks

# getting the most important one to show the user their next task
# most important is always in the first slot in the heap
@app.get("/api/most_important")
def get_most_impotant():
    if task_heap:
        return task_heap[0][2]

    return {
        "message": "No tasks in your list."
    }

# adding a task 
@app.post("/api/add_task")
async def add_task(task: Task):
    # we are doing to use our global data pandas file 
    global data 
    deadline = pd.to_datetime(task.deadline)
    created_at = datetime.now() 

    # if the user forgot to provide any priority our AI model will predict and we will use that
    predicted_priority_from_AI = predict_priority(deadline, created_at, task.estimation)

    if task.importance: 
        importance = task.importance
    else:
        importance = predicted_priority_from_AI

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
def save():
    data.to_csv("dataset/sample_task_dataset.csv", index=False)
    return {"message": "Tasks saved successfully!"}