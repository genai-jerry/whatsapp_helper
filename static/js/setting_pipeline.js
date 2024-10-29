class SettingPipeline {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Listen for assign button clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('assign-btn')) {
                this.handleAssignment(e);
            }
        });

        
    }

    async handleAssignment(event) {
        const button = event.target;
        const opportunityId = button.dataset.opportunityId;
        const employeeId = document.getElementById('employeeSelect').value;

        if (!employeeId) {
            alert('Please select an employee first');
            return;
        }

        try {
            button.disabled = true;
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Assigning...';

            const response = await fetch('/review/call-setting/assign-lead', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    opportunity_id: opportunityId,
                    employee_id: employeeId
                })
            });

            const data = await response.json();

            if (response.ok) {
                // Success handling
                this.moveOpportunityToAssigned(opportunityId);
                button.innerHTML = 'Assigned';
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
            } else {
                // Error handling
                throw new Error(data.message || 'Failed to assign opportunity');
            }
        } catch (error) {
            console.error('Assignment failed:', error);
            button.disabled = false;
            button.innerHTML = 'Assign';
            alert('Failed to assign opportunity: ' + error.message);
        }
    }

    moveOpportunityToAssigned(opportunityId) {
        // Find the opportunity row in the pipeline section
        const opportunityRow = document.querySelector(`tr[data-opportunity-id="${opportunityId}"]`);
        if (!opportunityRow) return;

        // Clone the row
        const clonedRow = opportunityRow.cloneNode(true);
        
        // Update the assign button in the cloned row
        const assignButton = clonedRow.querySelector('.assign-btn');
        if (assignButton) {
            assignButton.innerHTML = 'Assigned';
            assignButton.disabled = true;
            assignButton.classList.remove('btn-primary');
            assignButton.classList.add('btn-success');
        }

        // Find the appropriate assigned leads table based on the opportunity's status
        const status = opportunityRow.dataset.status || 'new-leads';
        const targetTableId = status === 'follow-up' ? 'followUpList' :
                            status === 'no-show' ? 'noShowsList' :
                            'newLeadsList';

        // Add to assigned section
        const targetTable = document.querySelector(`#${targetTableId} tbody`);
        if (targetTable) {
            targetTable.appendChild(clonedRow);
        }

        // Remove from pipeline section
        opportunityRow.remove();

        // Update counts if they exist
        this.updateCounts();
    }

    updateCounts() {
        // Update the counts in both sections if count elements exist
        const sections = ['new-leads', 'follow-up', 'no-show'];
        
        sections.forEach(section => {
            const pipelineCount = document.querySelector(`#pipeline-${section}-count`);
            const assignedCount = document.querySelector(`#assigned-${section}-count`);
            
            if (pipelineCount) {
                const count = document.querySelector(`#pipelinePipeline tr[data-status="${section}"]`).length;
                pipelineCount.textContent = count;
            }
            
            if (assignedCount) {
                const count = document.querySelector(`#${section}List tr[data-status="${section}"]`).length;
                assignedCount.textContent = count;
            }
        });
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.settingPipeline = new SettingPipeline();
});


const employeeSelect = document.getElementById('employeeSelect');

employeeSelect.addEventListener('change', function() {
    const selectedUserId = this.value;
    if (selectedUserId) {
        window.location.href = `/review/${destination}/${selectedUserId}`;
    }
});