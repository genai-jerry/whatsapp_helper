class LeadAppointment {
    constructor(){
        this.pipelineAppointments = {};
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Listen for assign button clicks
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('assign-appt-btn')) {
                this.assignCallSetterToAppointment(e);
            }
        });
    }

    async assignCallSetterToAppointment(event) {
        try {
            const button = event.target;
            await this.addAssignAppointmentHandler(button);
        } catch (error) {
            console.error('Assignment failed:', error);
        }
    }
    
    async addAssignAppointmentHandler(button) {
        try {
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

    handleAppointment(element){
        const containedList = element.closest('.pipeline-appt-list');
        const cardBody = containedList.closest('.card-body');
        if (!this.pipelineAppointments['card_body']) {
            this.pipelineAppointments['card_body'] = containedList.closest('.card-body');
        }

        const page = element.getAttribute('data-page');
        const pageArgs = element.getAttribute('data-page-args');
        const selectedEmployeeId = element.getAttribute('data-selected-employee-id');
        
        const params = new URLSearchParams();
        params.append('type', 'pipeline_appointments');
        params.append(pageArgs, page);
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }
        
        // Add loading effect
        this.pipelineAppointments['card_body'].classList.add('loading-blur'); 

        this.handlePipelineApptPageClick(page, cardBody, pageArgs, params);
    }

    handlePipelineApptPageClick(page, cardBody, pageArgs, params){
        const appointmentsTBody = $(cardBody).find('tbody')[0];
        const templateRow = $(cardBody).find('.pipeline-appt-item')[0];

        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            this.refreshAppointments(json, cardBody, appointmentsTBody, templateRow, page, pageArgs);
        })
        .catch(error => {
            console.error('Error fetching appointment pagination data:', error);
        })
        .finally(() => {
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
                const templateItem = templateRow.cloneNode(true);

                // Update opportunity link and name
                const opportunityLink = templateItem.querySelector('a[href^="/opportunity/"]');
                opportunityLink.href = `/opportunity/${appointment.opportunity_id}`;
                opportunityLink.title = appointment.opportunity_name;
                opportunityLink.textContent = appointment.opportunity_name.length > 15 ? 
                    appointment.opportunity_name.substring(0, 15) + '...' : 
                    appointment.opportunity_name;

                // Update appointment time
                const appointmentTimeSpan = templateItem.querySelector('.bi-calendar')?.closest('.badge');
                if (appointmentTimeSpan) {
                    const timeText = appointmentTimeSpan.childNodes[appointmentTimeSpan.childNodes.length - 1];
                    timeText.textContent = formatDateTime(appointment.appointment_time);
                }

                // Update ad name if exists
                const adNameSpan = templateItem.querySelector('.bi-megaphone')?.closest('.badge');
                if (adNameSpan) {
                    if (appointment.ad_name) {
                        adNameSpan.setAttribute('title', appointment.ad_name);
                        const adNameText = adNameSpan.childNodes[adNameSpan.childNodes.length - 1];
                        adNameText.textContent = appointment.ad_name.length > 10 ? 
                            appointment.ad_name.substring(0, 10) + '...' : 
                            appointment.ad_name;
                    } else {
                        adNameSpan.remove();
                    }
                }

                // Update assign button
                const assignButton = templateItem.querySelector('.assign-appt-btn');
                if (assignButton) {
                    assignButton.setAttribute('data-appointment-id', appointment.appointment_id);
                    assignButton.setAttribute('title', 'Assign');
                    assignButton.classList.remove('btn-success');
                    assignButton.classList.add('btn-outline-primary');
                    assignButton.textContent = 'Assign';
                    assignButton.onclick = () => window.settingPipeline.addAssignAppointmentHandler(assignButton);
                }

                appointmentsTBody.appendChild(templateItem);
            });

            // Update pagination
            const pageNav = $(cardBody).find('nav[aria-label="pagination"]')[0];
            window.callSettingPagination.updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs); 

            // Reinitialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.leadAppointment = new LeadAppointment();
});