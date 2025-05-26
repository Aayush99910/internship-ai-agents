# first importing necessary libraries
import heapq
import pandas as pd 
from datetime import datetime
from model_functions import predict_priority

def load_data():
    # importing the csv file from pandas into a dataframe
    file = pd.read_csv("dataset/sample_task_dataset.csv", parse_dates=["Deadline", "Date Created"])
    return file 

# mapping High, Medium and Low to number for heap data structure
def map_importance_to_number(importance):
    # 1 will be the highest and then 3 will be the lowest
    if importance.lower() == "high":
        return 2
    elif importance.lower() == "medium":
        return 1 
    else:
        return 0 
    
# heap data structure for dynamic updates 
def build_heap(data):
    task_heap = []
    heapq.heapify(task_heap)
    for _ , row in data.iterrows():
        priority = map_importance_to_number(row["Importance"])
        heapq.heappush(task_heap, (row["Deadline"], -1 * priority, row.to_dict()))
    return task_heap

# add task functionality for users
def add_task(data, task_heap):
    name = input("Task name: ")
    deadline = pd.to_datetime(input("Deadline (YYYY-MM-DD HH:MM): "))
    estimation = input("Estimation time (e.g., 120 mins): ")
    created_at = datetime.now()

    # predicting the task priority and asking the user
    predicted_importance = predict_priority(deadline, created_at, estimation)
    print(f"AI suggests that this task is {predicted_importance} priority")

    # asking the user if they agree or want to add their own
    user_choice = input(f"Do you want to use this? (Y/n): ").strip().lower()
    if user_choice == 'n':
        importance = input("Enter your own importance (High/Medium/Low): ")
    else:
        importance = predicted_importance

    description = input("Description: ")
    status = input("Status (Not Started/In Progress/Completed): ")

    new_task = {
        "Task Name": name,
        "Deadline": deadline,
        "Importance": importance,
        "Description": description,
        "Date Created": created_at,
        "Estimation Time": estimation,
        "Status": status
    }
    

    data.loc[len(data)] = new_task
    priority = map_importance_to_number(importance)
    heapq.heappush(task_heap, (deadline, -1 * priority, new_task))
    print("Task added successfully!") 

# shows all the task in the todo
def show_all_tasks(task_heap):
    print("All Tasks (Prioritized):")
    sorted_heap = sorted(task_heap)
    for i, (_, _, task) in enumerate(sorted_heap, 1):
        print(f"{i}. {task['Task Name']} | Due: {task['Deadline']} | Priority: {task['Importance']} | Status: {task['Status']}")

# shows the most important task that the user needs to do next
def show_most_important(task_heap):
    if task_heap:
        _, _, task = task_heap[0]
        print("Most Important Task: ")
        print(f"{task['Task Name']} | Due: {task['Deadline']} | Priority: {task['Importance']} | Status: {task['Status']}\n")
    else:
        print("No tasks in your list.")

# saving the data to csv and exiting from the CLI
def save_and_exit(data):
    data.to_csv("dataset/sample_task_dataset.csv", index=False)
    print("Tasks saved. Exiting...")
    exit()