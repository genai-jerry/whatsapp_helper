// Function to list all pending tasks for a given opportunity
function listTasks(opportunity_id, for_all=false) {
    const tableBody = document.getElementById('taskListTableBody');
    if (!tableBody) {
        console.error('Task list table body not found');
        return;
    }
    
    tableBody.innerHTML = ''; // Clear existing rows
    let url = '/task?';
    if (opportunity_id != null) {
        url += `opportunity_id=${opportunity_id}`;
    }

    const employee_id = $('#employeeSelect')?.val();
    if (employee_id && employee_id != '' && !for_all) {
        url += `&employee_id=${employee_id}`;
    }
    // Fetch task data from the server
    fetch(url)
        .then(
            response => response.json()
        )
        .then(data => {
            const tasks = data.tasks;
            tasks.forEach(task => {
                const dueDate = new Date(task.due_date);
                const formattedDueDate = dueDate.toLocaleDateString('en-GB', {
                    weekday: 'long',
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric'
                });
                const formattedLastUpdated = new Date(task?.last_updated).toLocaleDateString('en-GB', {
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
                     <td>
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="taskStatus${task.id}" 
                                ${task.status == 1 ? 'checked' : ''}
                                onchange="updateTaskStatus(${task.id}, this.checked)">
                        </div>
                    </td>
                    <td>${task.last_updated != null ? formattedLastUpdated : 'N/A'}</td>
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
    document.getElementById('opportunityName').value = opportunity_name !== undefined ? opportunity_name : '';
    createTaskModal.show();
}

// Function to create a new task
function createTask() {
    const employee_id = $('#employeeSelect')?.val();
    if (employee_id && employee_id != '') {
        $('#taskEmployeeId').val(employee_id);
    }
    const form = document.getElementById('createTaskForm');
    const formData = new FormData(form);
    const taskFeedback = document.getElementById('taskFeedback');

    fetch('/task', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        taskFeedback.classList.remove('alert-danger');
        taskFeedback.classList.add('alert-success');
        taskFeedback.textContent = data.message;
        
        setTimeout(() => {
            const createTaskModal = bootstrap.Modal.getInstance(document.getElementById('createTaskModal'));
            createTaskModal.hide();
            listTasks(document.getElementById('taskOpportunityId').value);
            form.reset();
        }, 1500);
        
        taskFeedback.style.display = 'block';
        setTimeout(() => {
            taskFeedback.style.display = 'none';
            form.reset();
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

function updateTaskStatus(taskId, isComplete) {
    const status = isComplete ? 1 : 0;
    fetch(`/task/${taskId}/status`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .catch(error => {
        console.error('Error:', error);
        // Revert the switch if there was an error
        document.getElementById(`taskStatus${taskId}`).checked = !isComplete;
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

$(document).ready(function() {
    var taskFeedback = $('#taskFeedback');
  
    function showFeedback(message, isSuccess) {
      taskFeedback.removeClass('alert-success alert-danger').addClass(isSuccess ? 'alert-success' : 'alert-danger');
      taskFeedback.text(message).show();
      setTimeout(function() {
        taskFeedback.hide();
      }, 5000);
    }
    $('#submitCreateTask').click(function() {
      var form = $('#createTaskForm');
      var formData = new FormData(form[0]);
  
      $.ajax({
        url: '/task',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
          showFeedback(response.message, true);
          form[0].reset();
          opportunityList.empty();
          selectedOpportunityId.val('');
          setTimeout(function() {
            // clear the form data
            $('#createTaskModal').modal('hide');
            form.reset();  
            opportunityList.empty();
            selectedOpportunityId.val('');
          }, 2000);
        },
        error: function(xhr, status, error) {
          console.error(error);
          showFeedback('An error occurred while creating the task. Please try again.', false);
        }
      });
    });
  });
