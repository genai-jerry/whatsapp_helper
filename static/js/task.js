// Function to list all pending tasks for a given opportunity
function listTasks(opportunity_id) {
    const tableBody = document.getElementById('taskListTableBody');
    if (!tableBody) {
        console.error('Task list table body not found');
        return;
    }
    
    tableBody.innerHTML = ''; // Clear existing rows

    // Fetch task data from the server
    fetch(`/task?opportunity_id=${opportunity_id}`)
        .then(response => response.json())
        .then(tasks => {
            tasks.forEach(task => {
                const dueDate = new Date(task.due_date);
                const formattedDueDate = dueDate.toLocaleDateString('en-GB', {
                    weekday: 'long',
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric'
                });
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${task.opportunity_name}</td>
                    <td>${task.description}</td>
                    <td>${task.creator_name}</td>
                    <td>${formattedDueDate}</td>
                    <td>${task.status == 1 ? 'Completed' : 'Pending'}</td>
                    <td>${task.last_updated != null ? task.last_updated : 'N/A'}</td>
                `;
                tableBody.appendChild(row);
            });
            
            // Show the modal after populating the table
            const taskListModal = new bootstrap.Modal(document.getElementById('taskListModal'));
            taskListModal.show();
        })
        .catch(error => console.error('Error fetching tasks:', error));
}

// Function to show the create task modal
function showCreateTaskModal(opportunity_id, opportunity_name) {
    const createTaskModal = new bootstrap.Modal(document.getElementById('createTaskModal'));
    document.getElementById('taskOpportunityId').value = opportunity_id;
    document.getElementById('opportunityName').value = opportunity_name;
    createTaskModal.show();
}

// Function to create a new task
function createTask() {
    const form = document.getElementById('createTaskForm');
    const formData = new FormData(form);
    const taskFeedback = document.getElementById('taskFeedback');

    fetch('/task', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            taskFeedback.classList.remove('alert-danger');
            taskFeedback.classList.add('alert-success');
            taskFeedback.textContent = 'Task created successfully';
            form.reset();
            setTimeout(() => {
                const createTaskModal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
                createTaskModal.hide();
                listTasks(document.getElementById('taskOpportunityId').value);
            }, 1500);
        } else {
            taskFeedback.classList.remove('alert-success');
            taskFeedback.classList.add('alert-danger');
            taskFeedback.textContent = 'Error creating task: ' + data.message;
        }
        taskFeedback.style.display = 'block';
        setTimeout(() => {
            taskFeedback.style.display = 'none';
        }, 3000);
    })
    .catch(error => {
        console.error('Error creating task:', error);
        taskFeedback.classList.remove('alert-success');
        taskFeedback.classList.add('alert-danger');
        taskFeedback.textContent = 'Error creating task. Please try again.';
        taskFeedback.style.display = 'block';
    });
}

// Ensure the DOM is fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the button that opens the task list modal
    const openListModalBtn = document.querySelector('[data-bs-target="#taskListModal"]');
    if (openListModalBtn) {
        openListModalBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const opportunityId = this.getAttribute('data-opportunity-id');
            listTasks(opportunityId);
        });
    }

    // Add event listener for the button that opens the create task modal
    const openCreateModalBtn = document.querySelector('[data-bs-target="#createTaskModal"]');
    if (openCreateModalBtn) {
        openCreateModalBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const opportunityId = this.getAttribute('data-opportunity-id');
            const opportunityName = this.getAttribute('data-opportunity-name');
            showCreateTaskModal(opportunityId, opportunityName);
        });
    }
});
