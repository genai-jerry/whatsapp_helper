class TaskList {
    updateAssignedTaskList(newRow, lead) {
        // Update task elements based on _list_tasks.html structure
        const taskListButtons = newRow.querySelectorAll('.task-comment-btn');
        taskListButtons.forEach(button => {
            if (button.hasAttribute('onclick')) {
                const onclickAttr = button.getAttribute('onclick');
                if (onclickAttr.includes('listTasks')) {
                    button.setAttribute('onclick', `listTasks(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('showCreateTaskModal')) {
                    button.setAttribute('onclick', `showCreateTaskModal(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('listComments')) {
                    button.setAttribute('onclick', `listComments(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('showCreateCommentModal')) {
                    button.setAttribute('onclick', `showCreateCommentModal(${lead.id}, '${lead.name}')`);
                }
            }
            
            // Reinitialize tooltip for each button
            const buttonTooltip = button.querySelector('[data-bs-toggle="tooltip"]');
            if (buttonTooltip) {
                new bootstrap.Tooltip(buttonTooltip);
            }
        });
    }
}

window.taskList = new TaskList();