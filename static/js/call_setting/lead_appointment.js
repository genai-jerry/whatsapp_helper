class LeadAppointment {
    constructor(){
        this.pipelineAppointments = {};
        this.rowElement = {};
        this.navElement = {};
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
            const parentLeadList = button.closest('.leads-list');
            const elementId = parentLeadList.id;
            if (!employee_id) {
                alert('Please select an employee first');
                return;
            }
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
                const assignedElementId = elementId.replace('pipeline', 'assigned');
                window.assignedAppointment.handleAppointment(assignedElementId);
            } else {
                throw new Error(data.message || 'Failed to assign appointment');
            }
        } catch (error) {
            console.error('Assignment failed:', error);
        }
    }

    async handleAppointment(element_id, param_args = null){
        if (!this.pipelineAppointments[element_id]) {
            const element = $(`#${element_id}`)[0];
            const containedList = element.closest('.pipeline-appt-list');
            this.pipelineAppointments[element_id] = containedList.closest('.card');
            this.rowElement[element_id] = $(element).find('.pipeline-appt-item')[0];
            this.navElement[element_id] = $(element).find('.pagination')[0];
        }   

        const selectedEmployeeId = document.getElementById('employeeSelect').value;

        const params = new URLSearchParams();
        params.append('type', element_id);

        if(param_args){
            Object.keys(param_args).forEach(key => {
                params.append(key, param_args[key]);
            });
        }
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }

        return new Promise((resolve, reject) => {
            const card = this.pipelineAppointments[element_id];
            const templateRow = this.rowElement[element_id].cloneNode(true);
            card.classList.add('loading-blur');
            const tableBody = $(card).find('tbody')[0];
            tableBody.appendChild(templateRow);
            this.loadAppointments(params, card, tableBody, templateRow, selectedEmployeeId)
                .then(totalCount => {
                    const newNavElement = this.navElement[element_id].cloneNode(true);
                    $(card).find('.pagination')[0].replaceWith(newNavElement);
                    resolve([totalCount, card]);
                    card.classList.remove('loading-blur');
                })
                .catch(error => {
                    reject(error);
                }).finally(() => {
                    setTimeout(() => {
                        card.classList.remove('loading-blur');
                    }, 300);
                });;
        });
    }

    async loadAppointments(params, card, appointmentsTbody, templateRow, selectedEmployeeId){
        return new Promise((resolve, reject) => {
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(json => {
                return this.refreshAppointments(json, card, appointmentsTbody, templateRow);
            })
            .then(totalCount => {
                resolve(totalCount);
            })
            .catch(error => {
                console.error('Error fetching appointment pagination data:', error);
                reject(error);
            })
        });
    }

    async refreshAppointments(json, card, appointmentsTBody, templateRow){
        return new Promise((resolve, reject) => {
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
                // Get the parent card and update the text value of element with class items_count
                const parentCard = $(card).closest('.card');
                const itemsCount = $(parentCard).find('.items_count')[0];
                itemsCount.textContent = json.total_count;
                // Reinitialize tooltips
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
                resolve(json.total_count);
            }
        });
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.leadAppointment = new LeadAppointment();
});