class AssignedLead {
    constructor() {
        this.assignedElements = {};
        this.rowElement = {}
        this.navElement = {}
        this.params = new URLSearchParams();
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

    async handleAssigned(element_id, param_args = null) {
        
        if (!this.assignedElements[element_id]) {
            const element = $(`#${element_id}`)[0];
            const containedList = element.closest('.assigned-list');
            this.assignedElements[element_id] = containedList.closest('.card');
            this.rowElement[element_id] = $(element).find('.assigned-item')[0];
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
            const card = this.assignedElements[element_id];
            const templateRow = this.rowElement[element_id].cloneNode(true);
            card.classList.add('loading-blur');
            const tableBody = $(card).find('tbody')[0];
            tableBody.appendChild(templateRow);
            this.loadAssignedLeads(this.params, card, tableBody, templateRow, selectedEmployeeId)
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

    async loadAssignedLeads(params, cardBody, assignedTbody, templateRow, selectedEmployeeId) {
        return new Promise((resolve, reject) => {
            fetch(`/review/call-setting${selectedEmployeeId ? '/' + selectedEmployeeId : ''}?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(json => {
                return this.refreshLeads(json, cardBody, assignedTbody, templateRow, params.get('type'));
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

    async refreshLeads(json, cardBody, assignedTbody, templateRow, type){
        return new Promise((resolve, reject) => {
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
                    if (opportunity.call_status != 8 || type != 'assigned_no_show') {
                        this.updateAssignedSelectStatus(newRow, opportunity);
                    }
                        
                    // Update task list buttons
                    window.taskList.updateAssignedTaskList(newRow, opportunity);

                    // Update timer
                    this.updateAssignedTimer(newRow, opportunity);
                        
                    assignedTbody.appendChild(newRow);
                });

                // Get the parent card and update the text value of element with class items_count
                const parentCard = $(cardBody).closest('.card');
                const itemsCount = $(parentCard).find('.items_count')[0];
                itemsCount.textContent = json.total_count;
                // Reinitialize tooltips
                var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl)
                });
                resolve(json.total_count);
            }
        });
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
            $('#appointments-booked-today').text(parseInt($('#appointments-booked-today').text()) + 1);
        }else{
            $('#calls-made-today').text(parseInt($('#calls-made-today').text()) + 1);
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
