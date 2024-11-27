class LeadPipeline {
    constructor() {
        this.pipelineElements = {};
        this.rowElement = {};
        this.navElement = {};
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
        const employeeId = $('#employeeSelect').val();
        const parentLeadList = button.closest('.leads-list');
        const elementId = parentLeadList.id;
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
                const assignedElementId = elementId.replace('pipeline', 'assigned');
                window.assignedLead.handleAssigned(assignedElementId);
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

    async handlePipeline(element_id, param_args = null) {
        if (!this.pipelineElements[element_id]) {
            const element = $(`#${element_id}`)[0];
            const containedList = element.closest('.pipeline-list');
            this.pipelineElements[element_id] = containedList.closest('.card');
            this.rowElement[element_id] = $(element).find('.pipeline-item')[0];
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
            const card = this.pipelineElements[element_id];
            const templateRow = this.rowElement[element_id].cloneNode(true);
            card.classList.add('loading-blur');
            const tableBody = $(card).find('tbody')[0];
            tableBody.appendChild(templateRow);
            this.loadLeads(params, card, tableBody, templateRow, selectedEmployeeId)
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

    async loadLeads(params, card, pipelineTbody, templateRow, selectedEmployeeId) {
        return new Promise((resolve, reject) => {
            fetch(`/review/call-setting?${params.toString()}`, {
                method: 'GET',
            headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(json => {
                return this.refreshLeads(json, card, pipelineTbody, templateRow);
            })
            .then(totalCount => {
                resolve(totalCount);
            })
            .catch(error => {
                console.error('Error fetching pagination data:', error);
                reject(error);
            })
        });
    }

    async refreshLeads(json, card, pipelineTbody, templateRow) {
        return new Promise((resolve, reject) => {
            if (pipelineTbody) {
            $(pipelineTbody).find('tr').each(function() {
                $(this).remove();
                });
                
                json.items.forEach(lead => {
                    const newRow = templateRow.cloneNode(true);
                    
                    // Update opportunity link and name
                    const opportunityLink = newRow.querySelector('a[href^="/opportunity/"]');
                    opportunityLink.href = `/opportunity/${lead.id}`;
                    opportunityLink.title = lead.name;
                    opportunityLink.textContent = lead.name.length > 15 ? lead.name.substring(0, 15) + '...' : lead.name;
                    
                    const registerTimeSpan = newRow.querySelectorAll('.register-time')[0];
                    registerTimeSpan.lastChild.textContent = formatDateWithMonth(lead.register_time);
                    
                    // Update last updated time
                    const lastUpdatedSpan = newRow.querySelector('.bi-telephone-outbound')?.closest('.badge');
                    if (lastUpdatedSpan) {
                        if (lead.last_updated) {
                            const lastUpdatedText = lastUpdatedSpan.childNodes[lastUpdatedSpan.childNodes.length - 1];
                            lastUpdatedText.textContent = formatDateTime(lead.last_updated);
                        } else {
                            lastUpdatedSpan.closest('p').remove();
                        }
                    }
                    
                    // Update ad name
                    const adNameSpan = newRow.querySelector('.bi-megaphone')?.closest('.badge');
                    if (adNameSpan) {
                        if (lead.ad_name) {
                            adNameSpan.setAttribute('title', lead.ad_name);
                            const adNameText = adNameSpan.childNodes[adNameSpan.childNodes.length - 1];
                            adNameText.textContent = lead.ad_name.length > 10 ? lead.ad_name.substring(0, 10) + '...' : lead.ad_name;
                        } else {
                            adNameSpan.closest('p').remove();
                        }
                    }
                    // Update setter button
                    this.updateAssignSetter(newRow, lead);
                    
                    $(pipelineTbody).append(newRow);
                });

                // Get the parent card and update the text value of element with class items_count
                const parentCard = $(card).closest('.card');
                const itemsCount = $(parentCard).find('.items_count')[0];
                itemsCount.textContent = json.total_count;

                // Reinitialize tooltips
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl)
                });
            }
            resolve(json.total_count);
        });
    }

    updateAssignSetter(newRow, lead) {
        // Update setter button
        const setterButton = newRow.querySelector('.set-call');
        if (setterButton) {
            setterButton.setAttribute('onclick', `assignCallSetter('${lead.id}')`);
            setterButton.setAttribute('title', 'Assign Setter');
            setterButton.classList.add('btn-outline-primary');
            setterButton.textContent = 'Assign';
            setterButton.classList.add('disabled');
            
            // Make sure SVG icon has tooltip
            const svgIcon = setterButton.querySelector('.bi-check-lg');
            if (svgIcon) {
            svgIcon.setAttribute('data-bs-toggle', 'tooltip');
            svgIcon.setAttribute('data-bs-placement', 'top');
        }
        
        // Initialize tooltip
        const tooltip = setterButton.querySelector('[data-bs-toggle="tooltip"]');
            if (tooltip) {
                new bootstrap.Tooltip(tooltip);
            }
        }
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.leadPipeline = new LeadPipeline();
});


const employeeSelect = document.getElementById('employeeSelect');

employeeSelect.addEventListener('change', function() {
    const selectedUserId = this.value;
    if (selectedUserId) {
        window.location.href = `/review/${destination}/${selectedUserId}`;
    }
});