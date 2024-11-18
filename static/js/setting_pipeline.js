class SettingPipeline {
    constructor() {
        this.initializeEventListeners();
        this.initializeStatusSelects();
        this.initializeAppointmentStatusButtons();
    }

    initializeEventListeners() {
        // Listen for assign button clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('assign-btn')) {
                this.handleAssignment(e);
            }
            if (e.target.classList.contains('assign-appt-btn')) {
                this.assignCallSetterToAppointment(e);
            }
        });
    }

    async handleAssignment(event) {
        const button = event.target;
        const opportunityId = button.dataset.opportunityId;
        const employeeId = $('#employeeSelect').val();

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
                button.classList.add('btn-outline-success');
            } else {
                // Error handling
                throw new Error(data.message || 'Failed to assign opportunity');
            }
        } catch (error) {
            console.error('Assignment failed:', error);
            button.disabled = true;
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-danger');
            button.innerHTML = 'Already Assigned';
        }
    }

    async assignCallSetterToAppointment(event) {
        try {
            const button = event.target;
            const appointmentId = button.dataset.appointmentId;
            const employee_id = $('#employeeSelect').val();
            const response = await fetch(`/review/call-setting/assign-appointment`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    },
                body: JSON.stringify({
                    appointment_id: appointmentId,
                    employee_id: employee_id
                })
            });
            const data = await response.json();
            if (data.status === 'success') {
                button.innerHTML = 'Assigned';
                button.classList.remove('btn-primary');
                button.classList.add('btn-outline-success');
            } else {
                throw new Error(data.message || 'Failed to assign appointment');
            }
        } catch (error) {
            console.error('Assignment failed:', error);
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
            const status = select.value;
            
            // Check if parent td has no-shows class
            if (select.closest('td').classList.contains('no-shows')) {
                // unset the value of the select
                select.value = '';
                select.style.backgroundColor = 'white';
                select.style.color = 'black';
            }
        });
    }

    showCallSetterButton(select) {
        // Find and enable the nearest set-call button
        select.closest('tr').querySelector('.set-call').classList.remove('disabled');
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
    
    updateModifiedSelectStyling(select) {
        select.closest('tr').style.backgroundColor = '#e8f5e9';
    }

    checkCallBooked(select) {
        const status = select.value;
        if (status === '8') {
            select.closest('tr').style.backgroundColor = '#c8e6c9';
            this.showCallSetterButton(select);
        }
    }

    async handleStatusChange(event) {
        const select = event.target;
        const opportunityId = select.dataset.opportunityId;
        const newStatus = select.value;
        const employeeId = document.getElementById('employeeSelect').value;
        try {
            fetch(`/opportunity/status/${opportunityId}/call_status?employee_id=${employeeId}`, {
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
                    this.updateModifiedSelectStyling(select);
                    this.checkCallBooked(select);
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

    initializeAppointmentStatusButtons() {
        document.querySelectorAll('.confirm-call').forEach(button => {
            button.addEventListener('click', (e) => this.confirmAppointment(button));
        });
        document.querySelectorAll('.discovery-call-done').forEach(button => {
            button.addEventListener('click', (e) => this.markDiscoveryCallDone(button));
        });
    }

    async confirmAppointment(button) {
        const appointmentId = $(button).attr('data-appointment-id');
        try {
            button.disabled = true;
            const response = await fetch(`/appointment/${appointmentId}/confirm`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            });
            const data = await response.json();
            if (data.status === 'success') {
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                button.classList.add('disabled');
            } else {
                throw new Error(data.message || 'Failed to confirm appointment');
            }
        } catch (error) {
            console.error('Confirmation failed:', error);
        }
    }

    async markDiscoveryCallDone(button) {
        const appointmentId = $(button).data('appointment-id');
        const opportunityId = $(button).data('opportunity-id');
        try {
            button.disabled = true;
            const response = await fetch(`/appointment/status/${opportunityId}/${appointmentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    status: 10,
                })
            });
            const data = await response.json();
            if (data.status === 'success') {
                button.classList.remove('btn-primary');
                button.classList.add('btn-success');
                button.classList.add('disabled');
            }
        } catch (error) {
            console.error('Marking discovery call done failed:', error);
        }
    }
}

function assignCallSetter(opportunity_id) {
    try {
        const employee_id = $('#employeeSelect').val();
        fetch(`/opportunity/${opportunity_id}/call-setter/${employee_id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                },
        }).then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.status === 'success') {
                showSuccessToast('Call setter updated successfully');
            } else {
                showErrorToast('Failed to update call setter');
            }
        });
    } catch (error) {
        console.error('Assignment failed:', error);
    }
}

function showSuccessToast(message) {
    showToast(message, 'success');
}

function showErrorToast(message) {
    showToast(message, 'error');
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