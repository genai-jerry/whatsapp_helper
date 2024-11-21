class AssignedLead {
    constructor() {
        this.assignedElements = {};
        this.initializeStatusSelects();
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

    async handleAssigned(element) {
        const containedList = element.closest('.assigned-list');
        const type = containedList ? containedList.id : '';
        
        if (!this.assignedElements[type + '_card_body']) {
            this.assignedElements[type + '_card_body'] = containedList.closest('.card-body');
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

        this.assignedElements[type + '_card_body'].classList.add('loading-blur');
        this.handleAssignedPageClick(page, pageArgs, params, this.assignedElements[type + '_card_body'], selectedEmployeeId);
    }

    async handleAssignedPageClick(page, pageArgs, params, cardBody, selectedEmployeeId) {
        const assignedTbody = $(cardBody).find('tbody')[0];
        const templateRow = $(cardBody).find('.assigned-item')[0];
        fetch(`/review/call-setting${selectedEmployeeId ? '/' + selectedEmployeeId : ''}?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            this.refreshLeads(json, cardBody, assignedTbody, templateRow, page, pageArgs);
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

    refreshLeads(json, cardBody, assignedTbody, templateRow, page, pageArgs){
        if (assignedTbody) {
            $(assignedTbody).find('tr').each(function() {
                $(this).remove();
            });
            
            json.items.forEach(opportunity => {
                const newRow = templateRow.cloneNode(true);
                newRow.style.backgroundColor = 'white';
                // Update opportunity link and name
                const opportunityLink = newRow.querySelector('a[href^="/opportunity/"]');
                opportunityLink.href = `/opportunity/${opportunity.id}`;
                opportunityLink.title = opportunity.name;
                opportunityLink.textContent = opportunity.name.length > 15 ? 
                    opportunity.name.substring(0, 15) + '...' : 
                    opportunity.name;
                
                // Update phone number
                const phoneLink = newRow.querySelector('a[href^="tel:"]');
                phoneLink.href = `tel:${opportunity.phone}`;
                phoneLink.textContent = opportunity.phone;
                
                // Update register time
                const registerTimeSpan = newRow.querySelector('.bi-clock').closest('.badge');
                const registerTimeText = registerTimeSpan.childNodes[registerTimeSpan.childNodes.length - 1];
                registerTimeText.textContent = formatDateWithMonth(opportunity.register_time);
                    
                // Update last updated time
                const lastUpdatedSpan = newRow.querySelector('.bi-telephone-outbound')?.closest('.badge');
                if (lastUpdatedSpan) {
                    if (opportunity.last_updated) {
                        const lastUpdatedText = lastUpdatedSpan.childNodes[lastUpdatedSpan.childNodes.length - 1];
                        lastUpdatedText.textContent = formatDateTime(opportunity.last_updated);
                    } else {
                        lastUpdatedSpan.closest('p').remove();
                    }
                }
                
                // Update ad name
                this.updateAssignedAdName(newRow, opportunity);
                
                // Update status select
                if (opportunity.call_status != 8 || pageArgs != 'assigned_no_show_page') {
                    this.updateAssignedSelectStatus(newRow, opportunity);
                }
                
                // Update task list buttons
                window.taskList.updateAssignedTaskList(newRow, opportunity);

                // Update timer
                this.updateAssignedTimer(newRow, opportunity);
                
                assignedTbody.appendChild(newRow);
            });

            // Update pagination
            const pageNav = $(cardBody).find('nav[aria-label="pagination"]')[0];
            if (pageNav) {
                window.callSettingPagination.updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs);
            }
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

    updateAssignedAdName(newRow, lead) {
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
    }

    updateAssignedSelectStatus(newRow, lead) {
        // Update status select
        const statusSelect = newRow.querySelector('.status-select');
        if (statusSelect) {
            statusSelect.setAttribute('data-opportunity-id', lead.id);
            if (lead.call_status) {
                const selectedOption = statusSelect.querySelector(`option[value="${lead.call_status}"]`);
                if (selectedOption) {
                    selectedOption.selected = true;
                    const bgColor = selectedOption.getAttribute('data-bg-color');
                    const textColor = selectedOption.getAttribute('data-text-color');
                    statusSelect.style.backgroundColor = bgColor;
                    statusSelect.style.color = textColor;
                }
            }
            // Add change event listener to connect with SettingPipeline
            statusSelect.addEventListener('change', (e) => {
                this.handleStatusChange(e);
            });
        }
    }

    updateAssignedTimer(newRow, lead) {
        // Update timer
        const timerButton = newRow.querySelector('.callback-datetime');
        if (timerButton) {
            // Update button attributes
            timerButton.id = `callback-datetime-${lead.id}`;
            timerButton.setAttribute('data-opportunity-id', lead.id);
            timerButton.setAttribute('title', 'Specify Time');
            
            // Make sure SVG icon has tooltip
            const svgIcon = timerButton.querySelector('svg');
            if (svgIcon) {
                svgIcon.setAttribute('data-bs-toggle', 'tooltip');
                svgIcon.setAttribute('data-bs-placement', 'top');
            }
            initCallbackDatetime(timerButton);
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

    showCallSetterButton(select) {
        // Find and enable the nearest set-call button
        select.closest('tr').querySelector('.set-call').classList.remove('disabled');
    }
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.assignedLead = new AssignedLead();
});
