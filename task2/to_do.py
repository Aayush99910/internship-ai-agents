# first importing necessary libraries
import heapq
import pandas as pd 
from datetime import datetime

def load_data():
    # importing the csv file from pandas into a dataframe
    file = pd.read_csv("sample_task_dataset.csv", parse_dates=["Deadline", "Date Created"])
    return file 

# mapping High, Medium and Low to number for heap data structure
def map_importance_to_number(importance):
    # 1 will be the highest and then 3 will be the lowest
    if importance.lower() == "high":
        return 1 
    elif importance.lower() == "medium":
        return 2 
    else:
        return 3 
    
# heap data structure for dynamic updates 
def build_heap(data):
    task_heap = []
    heapq.heapify(task_heap)
    for _ , row in data.iterrows():
        priority = map_importance_to_number(row["Importance"])
        heapq.heappush(task_heap, (row["Deadline"], priority, row.to_dict()))
    return task_heap

# add task functionality for users
def add_task(data, task_heap):
    name = input("Task name: ")
    deadline = pd.to_datetime(input("Deadline (YYYY-MM-DD HH:MM): "))
    importance = input("Importance (High/Medium/Low): ")
    description = input("Description: ")
    created_at = datetime.now()
    estimation = input("Estimation time (e.g., 120 mins): ")
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
    heapq.heappush(task_heap, (deadline, priority, new_task))
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
    data.to_csv("sample_task_dataset.csv", index=False)
    print("Tasks saved. Exiting...")
    exit()

# main function for users to show the options
def main():
    data = load_data()
    task_heap = build_heap(data)

    while True:
        print("TO-DO MENU")
        print("1. Add new task")
        print("2. Show all tasks in your todo")
        print("3. Show the first task that you need to do (Most important)")
        print("4. Save and exit")
        user_choice = int(input("Enter a choice: "))

        if user_choice == 1:
            add_task(data, task_heap)
        elif user_choice == 2:
            show_all_tasks(task_heap)
        elif user_choice == 3:
            show_most_important(task_heap)
        elif user_choice == 4:
            save_and_exit(data)
        else:
            print("Invalid input! Try again.")

main()
