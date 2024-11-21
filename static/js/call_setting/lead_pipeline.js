class LeadPipeline {
    constructor() {
        this.pipelineElements = {};
        this.pipelineAppointments = {};
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

    async handlePipeline(element) {
        const containedList = element.closest('.pipeline-list');
        const type = containedList ? containedList.id : '';
        
        if (!this.pipelineElements[type + '_card_body']) {
            this.pipelineElements[type + '_card_body'] = containedList.closest('.card-body');
        }
        
        const page = element.getAttribute('data-page');
        const pageArgs = element.getAttribute('data-page-args');
        const selectedEmployeeId = element.getAttribute('data-selected-employee-id');
        
        const params = new URLSearchParams();
        params.append('type', type);
        params.append(pageArgs, page);
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }

        this.pipelineElements[type + '_card_body'].classList.add('loading-blur');
        this.handlePipelinePageClick(page, pageArgs, params, this.pipelineElements[type + '_card_body']);
    }

    async handlePipelinePageClick(page, pageArgs, params, cardBody) {
        const pipelineTbody = $(cardBody).find('tbody')[0];
        const templateRow = $(cardBody).find('.pipeline-item')[0];
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            this.refreshLeads(json, cardBody, pipelineTbody, templateRow, page, pageArgs);
        })
        .catch(error => {
            console.error('Error fetching pagination data:', error);
        })
        .finally(() => {
            // Remove loading effect
            setTimeout(() => {
                cardBody.classList.remove('loading-blur');
            }, 300);
        });
    }

    refreshLeads(json, cardBody, pipelineTbody, templateRow, page, pageArgs) {
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

            // Update pagination
            const pageNav = $(cardBody).find('nav')[0];
            window.callSettingPagination.updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs);
            // Get the parent card and update the text value of element with class items_count
            const parentCard = $(cardBody).closest('.card');
            const itemsCount = $(parentCard).find('.items_count')[0];
            itemsCount.textContent = json.total_count;

            // Reinitialize tooltips
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl)
            });
        }
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