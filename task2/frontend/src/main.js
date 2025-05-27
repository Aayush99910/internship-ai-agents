document.addEventListener('DOMContentLoaded', () => {
    const taskNameInput = document.getElementById('task-name');
    const deadlineInput = document.getElementById('deadline');
    const estimationInput = document.getElementById('estimation');
    const descriptionInput = document.getElementById('description');
    const statusSelect = document.getElementById('status');
    const importanceSelect = document.getElementById('importance');
    const prioritySuggestion = document.getElementById('priority-suggestion');
    const useSuggestedBtn = document.getElementById('use-suggested');
    const addTaskBtn = document.getElementById('add-task-btn');
    const taskList = document.getElementById('task-list');
    const mostImportantTask = document.getElementById('most-important-task');
    const saveExitBtn = document.getElementById('save-exit');

    // Fetch and display all tasks
    function fetchTasks() {
        fetch('https://internship-ai-agents.onrender.com/api/tasks')
            .then(response => response.json())
            .then(tasks => {
                taskList.innerHTML = '';
                tasks.forEach((task, index) => {
                    const taskCard = document.createElement('div');
                    taskCard.className = 'bg-white p-4 rounded-lg shadow-md';
                    taskCard.innerHTML = `
                        <h3 class="font-bold">${task['Task Name']}</h3>
                        <p><strong>Due:</strong> ${new Date(task['Deadline']).toLocaleString()}</p>
                        <p><strong>Priority:</strong> ${task['Importance']}</p>
                        <p><strong>Status:</strong> ${task['Status'] || 'Not Started'}</p>
                        <p>${task['Description'] || ''}</p>
                    `;
                    taskList.appendChild(taskCard);
                });
            })
            .catch(error => console.error('Error fetching tasks:', error));
    }

    // Fetch and display most important task
    function fetchMostImportant() {
        fetch('https://internship-ai-agents.onrender.com/api/most_important')
            .then(response => {
                if (response.ok) return response.json();
                throw new Error('No tasks');
            })
            .then(task => {
                mostImportantTask.innerHTML = `
                    <h3 class="font-bold">${task['Task Name']}</h3>
                    <p><strong>Due:</strong> ${new Date(task['Deadline']).toLocaleString()}</p>
                    <p><strong>Priority:</strong> ${task['Importance']}</p>
                    <p><strong>Status:</strong> ${task['Status'] || 'Not Started'}</p>
                    <p>${task['Description'] || ''}</p>
                `;
            })
            .catch(error => {
                mostImportantTask.innerHTML = '<p class="text-gray-600">No tasks in your list.</p>';
            });
    }

    // Predict priority when inputs change
    function predictPriority() {
        const deadline = deadlineInput.value;
        const estimation = estimationInput.value ? parseFloat(estimationInput.value) : null;
        if (deadline && estimation !== null) {
            const taskData = {
                deadline,
                estimation,
                dateCreated: new Date().toISOString()
            };

            fetch('https://internship-ai-agents.onrender.com/api/predict_priority', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskData)
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Priority prediction error:', data.error);
                    prioritySuggestion.textContent = 'Error predicting priority';
                } else {
                    prioritySuggestion.textContent = `AI suggests: ${data.priority} priority`;
                    useSuggestedBtn.style.display = 'inline-block';
                }
            })
            .catch(error => {
                console.error('Error predicting priority:', error);
                prioritySuggestion.textContent = 'Error predicting priority';
            });
        } else {
            prioritySuggestion.textContent = '';
            useSuggestedBtn.style.display = 'none';
        }
    }

    // Add task
    addTaskBtn.addEventListener('click', async () => {
        const estimation = estimationInput.value ? parseFloat(estimationInput.value) : null;
        const taskData = {
            taskName: taskNameInput.value,
            deadline: deadlineInput.value,
            estimation,
            description: descriptionInput.value || null,
            status: statusSelect.value || null,
            importance: importanceSelect.value || null
        };
        const response = await fetch('https://internship-ai-agents.onrender.com/api/add_task', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(taskData)
        })

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = response.json();
        alert(data.message);
        fetchTasks();
        fetchMostImportant();
        taskNameInput.value = '';
        deadlineInput.value = '';
        estimationInput.value = '';
        descriptionInput.value = '';
        statusSelect.value = 'Not Started';
        importanceSelect.value = 'Medium';
        prioritySuggestion.textContent = '';
        useSuggestedBtn.style.display = 'none';

    });

    // Use suggested priority
    useSuggestedBtn.addEventListener('click', () => {
        const suggestedPriority = prioritySuggestion.textContent.split(': ')[1]?.split(' ')[0];
        if (suggestedPriority) {
            importanceSelect.value = suggestedPriority;
        }
    });

    // Save and exit
    saveExitBtn.addEventListener('click', () => {
        fetch('https://internship-ai-agents.onrender.com/api/save', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => alert(data.message))
        .catch(error => console.error('Error saving:', error));
    });

    // Event listeners for priority prediction
    deadlineInput.addEventListener('change', predictPriority);
    estimationInput.addEventListener('input', predictPriority);

    // Initial fetch
    fetchTasks();
    fetchMostImportant();
});