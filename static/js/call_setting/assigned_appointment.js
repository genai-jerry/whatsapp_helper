class AssignedAppointment {
    constructor() {
        this.assignedAppointments = {};
        this.rowElement = {}
        this.navElement = {}
        this.params = new URLSearchParams();
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

    async handleAppointment(element_id, param_args = null){
        if (!this.assignedAppointments['card_body']) {
            const element = $(`#${element_id}`)[0];
            const containedList = element.closest('.assigned-appt-list');
            this.assignedAppointments['card_body'] = containedList.closest('.card-body');
            this.rowElement[element_id] = $(element).find('.assigned-appt-item')[0];
            this.navElement[element_id] = $(element).find('.pagination')[0];
        }   

        const selectedEmployeeId = document.getElementById('employeeSelect').value;
        
        this.params.set('type', element_id);

        if(param_args){
            Object.keys(param_args).forEach(key => {
                this.params.set(key, param_args[key]);
            });
        }
        if (selectedEmployeeId) {
            this.params.set('selected_employee_id', selectedEmployeeId);
        }

        return new Promise((resolve, reject) => {
            const card = this.assignedAppointments['card_body'];
            const templateRow = this.rowElement[element_id].cloneNode(true);
            card.classList.add('loading-blur');
            const tableBody = $(card).find('tbody')[0];
            tableBody.appendChild(templateRow);
            this.loadAssignedAppointments(this.params, card, 
                tableBody, 
                templateRow, 
                selectedEmployeeId)
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
                });
        });
    }

    async loadAssignedAppointments(params, card, appointmentsTBody, templateRow, selectedEmployeeId){
        return new Promise((resolve, reject) => {
            fetch(`/review/call-setting${selectedEmployeeId ? '/' + selectedEmployeeId : ''}?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(json => {
                return this.refreshAppointments(json, card, appointmentsTBody, templateRow);
            })
            .then(totalCount => {
                resolve(totalCount);
            })
            .catch(error => {
                console.error('Error fetching pagination data:', error);
                reject(error);
            })
            .finally(() => {
                // Remove loading effect
                setTimeout(() => {
                    cardBody.classList.remove('loading-blur');
                }, 300);
            });
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
                        if(appointment.ad_name){
                            adNameBadge.textContent = appointment.ad_name.length > 10 ? 
                                appointment.ad_name.substring(0, 10) + '...' : 
                                appointment.ad_name;
                            adNameBadge.setAttribute('title', appointment.ad_name);
                        }
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

                    appointmentsTBody.appendChild(newRow);
                });
            }
            // Get the parent card and update the text value of element with class items_count
            const parentCard = $(card).closest('.card');
            const itemsCount = $(parentCard).find('.items_count')[0];
            itemsCount.textContent = json.total_count;
            // Reinitialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            resolve(json.total_count);
        })
    }
}
// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.assignedAppointment = new AssignedAppointment();
});
