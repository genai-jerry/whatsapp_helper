class SettingPipeline {
    constructor() {
        this.initializeEventListeners();
        this.initializeStatusSelects();
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

            if (data.status === 'success') {
                // Success handling
                // this.moveOpportunityToAssigned(opportunityId);
                button.innerHTML = 'Assigned';
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
            } else {
                // Error handling
                throw new Error(data.message || 'Failed to assign opportunity');
            }
        } catch (error) {
            console.error('Assignment failed:', error);
            button.disabled = true;
            button.classList.remove('btn-primary');
            button.classList.add('btn-danger');
            button.innerHTML = 'Already Assigned';
        }
    }

   
    initializeStatusSelects() {
        document.querySelectorAll('.status-select').forEach(select => {
            // Set initial styling
            this.updateSelectStyling(select);

            // Add change event listener
            select.addEventListener('change', (e) => {
                this.handleStatusChange(e);
            });
        });
    }

    updateSelectStyling(select) {
        const selectedOption = select.options[select.selectedIndex];
        if (selectedOption && selectedOption.value) {
            select.style.backgroundColor = selectedOption.dataset.bgColor;
            select.style.color = selectedOption.dataset.textColor;
        } else {
            select.style.backgroundColor = '';
            select.style.color = '';
        }
    }

    async handleStatusChange(event) {
        const select = event.target;
        const opportunityId = select.dataset.opportunityId;
        const newStatus = select.value;

        try {
            fetch(`/opportunity/status/${opportunityId}/call_status`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status: newStatus,
                })
            }).then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    // Update the select styling
                    this.updateSelectStyling(select);
                } else {
                    select.value = select.dataset.previousValue;
                    this.updateSelectStyling(select);
                    alert('Failed to update status: ' + result.message);
                }
            });
        } catch (error) {
            console.error('Status update failed:', error);
            // Revert the select to its previous value
            alert('Failed to update status: ' + error.message);
        }
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