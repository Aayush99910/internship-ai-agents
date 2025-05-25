# importing all the functions
from task_functions import load_data, build_heap, add_task, show_all_tasks, show_most_important, save_and_exit

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
