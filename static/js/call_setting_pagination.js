// Add this at the top of your file

window.paginationInitialized = true;

document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for blur effect
    const style = document.createElement('style');
    style.textContent = `
        .loading-blur {
            filter: blur(2px);
            pointer-events: none;
            opacity: 0.6;
            transition: all 0.3s ease;
        }
    `;
    document.head.appendChild(style);

    function updatePagination(paginationNav, totalCount, currentPage, pageSize, pageArgs) {
        if (!paginationNav) return;

        const totalPages = Math.ceil(totalCount / pageSize);
        if (totalPages <= 1) {
            paginationNav.innerHTML = '';
            return;
        }

        const ul = paginationNav.querySelector('ul.pagination');
        ul.innerHTML = '';

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${currentPage == 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `
            <a id="previous-page-${pageArgs}" 
               data-page-args="${pageArgs}" 
               data-page="${currentPage-1}"
               class="page-link" 
               href="#"
               ${currentPage == 1 ? 'tabindex="-1" aria-disabled="true"' : ''}>
                Previous
            </a>`;
        ul.appendChild(prevLi);

        // First page
        const firstLi = document.createElement('li');
        firstLi.className = `page-item ${currentPage == 1 ? 'active' : ''}`;
        firstLi.innerHTML = `
            <a id="first-page-${pageArgs}" 
               data-page-args="${pageArgs}" 
               data-page="1"
               class="page-link" 
               href="#">1</a>`;
        ul.appendChild(firstLi);

        // Ellipsis if needed
        if (currentPage > 3) {
            const ellipsis1 = document.createElement('li');
            ellipsis1.className = 'page-item disabled';
            ellipsis1.innerHTML = `<span id="ellipsis1-${pageArgs}" class="page-link">...</span>`;
            ul.appendChild(ellipsis1);
        }

        // Current page (if not 1 or last)
        if (currentPage != 1 && currentPage != totalPages) {
            const currentLi = document.createElement('li');
            currentLi.className = 'page-item active';
            currentLi.innerHTML = `
                <a id="current-page-${pageArgs}" 
                   data-page-args="${pageArgs}" 
                   data-page="${currentPage}"
                   class="page-link" 
                   href="#">${currentPage}</a>`;
            ul.appendChild(currentLi);
        }

        // Ellipsis if needed
        if (currentPage < totalPages - 2) {
            const ellipsis2 = document.createElement('li');
            ellipsis2.className = 'page-item disabled';
            ellipsis2.innerHTML = `<span id="ellipsis2-${pageArgs}" class="page-link">...</span>`;
            ul.appendChild(ellipsis2);
        }

        // Last page
        if (totalPages > 1) {
            const lastLi = document.createElement('li');
            lastLi.className = `page-item ${currentPage == totalPages ? 'active' : ''}`;
            lastLi.innerHTML = `
                <a id="last-page-${pageArgs}" 
                   data-page-args="${pageArgs}" 
                   data-page="${totalPages}"
                   class="page-link" 
                   href="#">${totalPages}</a>`;
            ul.appendChild(lastLi);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage == totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <a id="next-page-${pageArgs}" 
               data-page-args="${pageArgs}" 
               data-page="${currentPage+1}"
               class="page-link" 
               href="#"
               ${currentPage == totalPages ? 'tabindex="-1" aria-disabled="true"' : ''}>
                Next
            </a>`;
        ul.appendChild(nextLi);

        // Reattach click handlers to new pagination links
        ul.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', handlePageClick);
        });
    }

    function handlePageClick(e) {
        e.preventDefault();
        const leadsList = this.closest('.leads-list');
        let isPipelineAppointment = false;
        let isPipeline = false;
        let isAssigned = false;
        let isAssignedAppointment = false;

        isPipeline = leadsList.classList.contains('pipeline-list');
        if (!isPipeline) {
            isAssigned = leadsList.classList.contains('assigned-list');
            if (!isAssigned) {
               isPipelineAppointment = leadsList.classList.contains('pipeline-appt-list');
               if (!isPipelineAppointment) {
                   isAssignedAppointment = leadsList.classList.contains('assigned-appt-list');
               }
            }
        }
        if (isPipeline || isAssigned ) {
            handlePipeline(this, isPipeline);
        }else if (isPipelineAppointment || isAssignedAppointment) {
            handleAppointment(this, isPipelineAppointment, leadsList);
        }
    }

    function handleAppointment(element, isPipelineAppointment, leadsList){
        const containedList = isPipelineAppointment ? element.closest('.pipeline-appt-list') : element.closest('.assigned-appt-list');
        const type = containedList ? containedList.id : '';
        const leadsTbody = containedList ? containedList.querySelector('tbody') : null;
        const cardBody = containedList.closest('.card-body');
        
        const page = element.getAttribute('data-page');
        const pageArgs = element.getAttribute('data-page-args');
        const selectedEmployeeId = element.getAttribute('data-selected-employee-id');
        
        const templateRow = isPipelineAppointment ? $('.pipeline-appt-item')[0] : $('.assigned-appt-item')[0];
        
        const params = new URLSearchParams();
        params.append('type', type);
        params.append(pageArgs, page);
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }
        
        // Add loading effect
        cardBody.classList.add('loading-blur'); 

        if (isPipelineAppointment) {
            handlePipelineApptPageClick(page, pageArgs, params, templateRow, cardBody);
        } else {
            handleAssignedApptPageClick(page, pageArgs, params, templateRow, cardBody, selectedEmployeeId);
        }
    }

    let pipelineElements = {};
    let assignedElements = {};

    function handlePipeline(element, isPipeline){
        const containedList = isPipeline ? element.closest('.pipeline-list') : element.closest('.assigned-list');
        const type = containedList ? containedList.id : '';

        
        if (isPipeline) {
            if (!pipelineElements[type + '_card_body']) {
                pipelineElements[type + '_card_body'] = containedList.closest('.card-body');
            }
        } else {
            if (!assignedElements[type + '_card_body']) {
                assignedElements[type + '_card_body'] = containedList.closest('.card-body');
            }
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
        

        if (isPipeline) {
            pipelineElements[type + '_card_body'].classList.add('loading-blur');
            handlePipelinePageClick(page, pageArgs, params, pipelineElements[type + '_card_body']);
        } else {
            assignedElements[type + '_card_body'].classList.add('loading-blur');
            handleAssignedPageClick(page, pageArgs, params, assignedElements[type + '_card_body'], selectedEmployeeId);
        }
    }
    

    function handlePipelinePageClick(page, pageArgs, params, cardBody) {
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
                    registerTimeSpan.lastChild.textContent = formatDate(lead.register_time);
                    
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
                    updateAssignedSetter(newRow, lead);
                    
                    $(pipelineTbody).append(newRow);
                });

                // Update pagination
                const pageNav = $(cardBody).find('nav')[0];
                updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs);
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

    function handleAssignedOpportunitySearch(searchInput){
        console.log(searchInput);
        const searchValue = $('#assigned_leads_search').val();
        console.log(searchValue);
        // Define the sections and their parameters
        const sections = [
            {
                containerId: 'assigned_appt_list',
                pageArgs: 'assigned_appt_page',
                templateClass: 'assigned-appt-item',
                type: 'assigned_appointments'
            },
            {
                containerId: 'assigned_leads',
                pageArgs: 'assigned_leads_page',
                templateClass: 'assigned-item',
                type: 'assigned'
            },
            {
                containerId: 'assigned_follow_up',
                pageArgs: 'assigned_follow_up_page',
                templateClass: 'assigned-item',
                    type: 'assigned'
            },
            {
            containerId: 'assigned_no_show',
                pageArgs: 'assigned_no_show_page',
                templateClass: 'assigned-item',
                type: 'assigned'
            }
        ];
        
        
        // Process each section
        sections.forEach(section => {
            const container = document.getElementById(section.containerId);
            if (container) {
                const selectedEmployeeId = $('#employeeSelect').val();
            
                // Create params
                const params = new URLSearchParams();
                params.append('type', section.containerId);
                params.append(section.pageArgs, '1'); // Start at page 1 for search
                params.append('search', searchValue);
                // Call handleAssignedPageClick with appropriate parameters
                if (section.type == 'leads') {
                    if (!pipelineElements[section.containerId + '_card_body']) {
                        pipelineElements[section.containerId + '_card_body'] = container.closest('.card-body');
                    }
                } else {
                    if (!assignedElements[section.containerId + '_card_body']) {
                        assignedElements[section.containerId + '_card_body'] = container.closest('.card-body');
                    }
                }

                if (section.type == 'assigned') {
                    assignedElements[section.containerId + '_card_body'].classList.add('loading-blur');
                    handleAssignedPageClick(
                        '1', // page number
                        section.pageArgs, 
                        params, 
                        assignedElements[section.containerId + '_card_body'],
                        selectedEmployeeId ? selectedEmployeeId : null
                    );
                } else {
                    assignedElements[section.containerId + '_card_body'].classList.add('loading-blur');
                    handleAssignedApptPageClick(
                        '1', // page number
                        section.pageArgs, 
                        params,
                        assignedElements[section.containerId + '_card_body'],
                        selectedEmployeeId ? selectedEmployeeId : null
                    );
                }
            }
        });
    }

    function handleAssignedPageClick(page, pageArgs, params, cardBody, selectedEmployeeId) {
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
                    registerTimeText.textContent = formatDate(opportunity.register_time);
                        
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
                    updateAssignedAdName(newRow, opportunity);
                    
                    // Update status select
                    if (opportunity.call_status != 8 || pageArgs != 'assigned_no_show_page') {
                        updateAssignedSelectStatus(newRow, opportunity);
                    }
                    
                    // Update task list buttons
                    updateAssignedTaskList(newRow, opportunity);

                    // Update timer
                    updateAssignedTimer(newRow, opportunity);
                    
                    assignedTbody.appendChild(newRow);
                });

                // Update pagination
                const pageNav = $(cardBody).find('nav[aria-label="pagination"]')[0];
                updatePagination(pageNav, json.total_count, parseInt(page), 10, pageArgs);
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

    function handlePipelineApptPageClick(page, pageArgs, params, templateRow, cardBody){
        appointmentsTbody = cardBody.querySelector('tbody');
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
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
                updatePagination(leadsList, json.total_count, parseInt(page), 10, pageArgs);

                // Reinitialize tooltips
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            }
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

    function handleAssignedApptPageClick(page, pageArgs, params, cardBody, selectedEmployeeId){
        appointmentsTbody = cardBody.querySelector('tbody');
        templateRow = cardBody.querySelector('.assigned-item')[0];
        fetch(`/review/call-setting${selectedEmployeeId ? '/' + selectedEmployeeId : ''}?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
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
                        appointmentTimeBadge.textContent = formatDate(appointment.appointment_time);
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
                    updateAssignedTaskList(newRow, {'id': appointment.opportunity_id, 'name': appointment.opportunity_name});

                    updatePagination(assignedList, json.total_count, parseInt(page), 10, pageArgs);

                    appointmentsTBody.appendChild(newRow);
                });

                // Reinitialize tooltips
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
            }
        }).finally(() => {
            // Remove loading effect
            setTimeout(() => {
                cardBody.classList.remove('loading-blur');
            }, 300);
        });
    }

    function updateAssignedSetter(newRow, lead) {
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
    
    function updateAssignedTimer(newRow, lead) {
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

    function updateAssignedAdName(newRow, lead) {
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

    function updateAssignedSelectStatus(newRow, lead) {
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
                window.settingPipeline.handleStatusChange(e);
            });
        }
    }

    function updateAssignedTaskList(newRow, lead) {
        // Update task elements based on _list_tasks.html structure
        const taskListButtons = newRow.querySelectorAll('.task-comment-btn');
        taskListButtons.forEach(button => {
            if (button.hasAttribute('onclick')) {
                const onclickAttr = button.getAttribute('onclick');
                if (onclickAttr.includes('listTasks')) {
                    button.setAttribute('onclick', `listTasks(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('showCreateTaskModal')) {
                    button.setAttribute('onclick', `showCreateTaskModal(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('listComments')) {
                    button.setAttribute('onclick', `listComments(${lead.id}, '${lead.name}')`);
                } else if (onclickAttr.includes('showCreateCommentModal')) {
                    button.setAttribute('onclick', `showCreateCommentModal(${lead.id}, '${lead.name}')`);
                }
            }
            
            // Reinitialize tooltip for each button
            const buttonTooltip = button.querySelector('[data-bs-toggle="tooltip"]');
            if (buttonTooltip) {
                new bootstrap.Tooltip(buttonTooltip);
            }
        });
    }
    
    function formatDate(dateString) {
        const date = new Date(dateString);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${String(date.getDate()).padStart(2, '0')} ${months[date.getMonth()]} ${date.getFullYear()}`;
    }
    
    function formatDateTime(dateString) {
        const date = new Date(dateString);
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${day} ${months[date.getMonth()]} ${date.getFullYear()} ${hours}:${minutes}`;
    }
    
    // Add initial event listeners
    $('.page-link').each(function() {
        $(this).unbind().click(handlePageClick);
    });
    $('#assigned_leads_search').unbind().keyup(handleAssignedOpportunitySearch);
});
