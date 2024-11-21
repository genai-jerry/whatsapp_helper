class AssignedAppointment {
    constructor() {
        this.assignedAppointments = {};
        this.initializeAppointmentStatusButtons();
    }
    initializeAppointmentStatusButtons() {
        document.querySelectorAll('.confirm-call').forEach(button => {
            this.addConfirmCallHandler(button);
        });
        document.querySelectorAll('.discovery-call-done').forEach(button => {
            this.addDiscoveryCallDoneHandler(button);
        });
    }

    addConfirmCallHandler(button) {
        button.addEventListener('click', (e) => this.confirmAppointment(button));
    }

    addDiscoveryCallDoneHandler(button) {
        button.addEventListener('click', (e) => this.markDiscoveryCallDone(button));
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

    async handleAppointment(element){
        const containedList = element.closest('.assigned-appt-list');
        if (!this.assignedAppointments['card_body']) {
            this.assignedAppointments['card_body'] = containedList.closest('.card-body');
        }   

        const page = element.getAttribute('data-page');
        const pageArgs = element.getAttribute('data-page-args');
        const selectedEmployeeId = element.getAttribute('data-selected-employee-id');

        const params = new URLSearchParams();
        params.append(pageArgs, page);
        params.append('type', 'assigned_appointments');
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }
        
        // Add loading effect
        this.assignedAppointments['card_body'].classList.add('loading-blur'); 

        await this.handleAssignedApptPageClick(page, pageArgs, params, this.assignedAppointments['card_body'], selectedEmployeeId);
    }

    async handleAssignedApptPageClick(page, pageArgs, params, cardBody, selectedEmployeeId){
        const appointmentsTBody = $(cardBody).find('tbody')[0];
        const templateRow = $(cardBody).find('.assigned-appt-item')[0];
        fetch(`/review/call-setting${selectedEmployeeId ? '/' + selectedEmployeeId : ''}?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            this.refreshAppointments(json, cardBody, appointmentsTBody, templateRow, page, pageArgs);
        }).finally(() => {
            // Remove loading effect
            setTimeout(() => {
                cardBody.classList.remove('loading-blur');
            }, 300);
        });
    }

    refreshAppointments(json, cardBody, appointmentsTBody, templateRow, page, pageArgs){
        if (appointmentsTBody) {
            // Clear existing appointments
            appointmentsTBody.querySelectorAll('tr').forEach(row => {
                row.remove();
            });
            json.items.forEach(appointment => {
                const newRow = templateRow.cloneNode(true);

                // Update appointment title
                const titleLink = newRow.querySelector('a[href^="/opportunity/"]');
                if (titleLink) {
                    titleLink.href = `/opportunity/${appointment.opportunity_id}`;
                    titleLink.textContent = appointment.opportunity_name;
                }

                // Update phone number
                const phoneButton = newRow.querySelector('a[href^="tel:"]');
                if (phoneButton) {
                    phoneButton.href = `tel:${appointment.opportunity_phone}`;
                    phoneButton.textContent = appointment.opportunity_phone;
                }

                // Update appointment time
                const appointmentTimeBadge = newRow.querySelector('.bi-calendar-event')?.closest('.badge');
                if (appointmentTimeBadge) {
                    appointmentTimeBadge.textContent = formatDateWithMonth(appointment.appointment_time);
                }

                // Update ad name
                const adNameBadge = newRow.querySelector('.bi-megaphone')?.closest('.badge');
                if (adNameBadge) {
                    adNameBadge.textContent = appointment.ad_name.length > 10 ? 
                        appointment.ad_name.substring(0, 10) + '...' : 
                        appointment.ad_name;
                    adNameBadge.setAttribute('title', appointment.ad_name);
                }

                // Update status buttons
                const confirmButton = newRow.querySelector('.confirm-call');
                if (confirmButton) {
                    confirmButton.id = `confirm-call-${appointment.appointment_id}`;
                    confirmButton.setAttribute('data-appointment-id', appointment.appointment_id);
                    confirmButton.classList.toggle('btn-success', appointment.confirmed);
                    confirmButton.classList.toggle('btn-primary', !appointment.confirmed);
                    confirmButton.disabled = appointment.confirmed;
                    confirmButton.onclick = () => window.settingPipeline.addConfirmCallHandler(confirmButton);
                }

                const discoveryButton = newRow.querySelector('.discovery-call-done');
                if (discoveryButton) {
                    discoveryButton.setAttribute('data-appointment-id', appointment.appointment_id);
                    discoveryButton.setAttribute('data-opportunity-id', appointment.opportunity_id);
                    discoveryButton.classList.remove('btn-success');
                    discoveryButton.classList.add('btn-primary');
                    discoveryButton.onclick = () => window.settingPipeline.addDiscoveryCallDoneHandler(discoveryButton);
                }

                // Update task list
                window.taskList.updateAssignedTaskList(newRow, {'id': appointment.opportunity_id, 'name': appointment.opportunity_name});

                const pageNav = $(cardBody).find('nav[aria-label="pagination"]')[0];
                window.callSettingPagination.updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs);

                appointmentsTBody.appendChild(newRow);
            });

            // Reinitialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }
}
// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.assignedAppointment = new AssignedAppointment();
});
