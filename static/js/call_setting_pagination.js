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

    function updatePagination(pipelineList, totalCount, currentPage, pageSize, pageArgs) {
        const paginationNav = pipelineList.querySelector('nav[aria-label="pagination"]');
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
        const isPipeline = leadsList.classList.contains('pipeline-list');
        const containedList = isPipeline ? this.closest('.pipeline-list') : this.closest('.assigned-list');
        const type = containedList ? containedList.id : '';
        const leadsTbody = containedList ? containedList.querySelector('tbody') : null;
        const cardBody = containedList.closest('.card-body');
        
        const page = this.getAttribute('data-page');
        const pageArgs = this.getAttribute('data-page-args');
        const selectedEmployeeId = this.getAttribute('data-selected-employee-id');
        
        const templateRow = isPipeline ? $('.pipeline-item')[0] : $('.assigned-item')[0];
        
        const params = new URLSearchParams();
        params.append('type', type);
        params.append(pageArgs, page);
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }
        
        // Add loading effect
        cardBody.classList.add('loading-blur');

        if (isPipeline) {
            handlePipelinePageClick(page, pageArgs, params, leadsList, templateRow, leadsTbody, cardBody);
        } else {
            handleAssignedPageClick(page, pageArgs, params, leadsList, templateRow, leadsTbody, cardBody);
        }
    }
    
    function handlePipelinePageClick(page, pageArgs, params, pipelineList, templateRow, pipelineTbody, cardBody) {
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            if (pipelineTbody) {
                pipelineTbody.querySelectorAll('tr').forEach(row => {
                    row.remove();
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
                    
                    pipelineTbody.appendChild(newRow);
                });

                // Update pagination
                updatePagination(pipelineList, json.total_count, parseInt(page), 10, pageArgs);

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

    function handleAssignedPageClick(page, pageArgs, params, assignedList, templateRow, assignedTbody, cardBody) {
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            if (assignedTbody) {
                assignedTbody.querySelectorAll('tr').forEach(row => {
                    row.remove();
                });
                
                json.items.forEach(lead => {
                    const newRow = templateRow.cloneNode(true);
                    newRow.style.backgroundColor = 'white';
                    // Update opportunity link and name
                    const opportunityLink = newRow.querySelector('a[href^="/opportunity/"]');
                    opportunityLink.href = `/opportunity/${lead.id}`;
                    opportunityLink.title = lead.name;
                    opportunityLink.textContent = lead.name.length > 15 ? lead.name.substring(0, 15) + '...' : lead.name;
                    
                    // Update phone number
                    const phoneLink = newRow.querySelector('a[href^="tel:"]');
                    phoneLink.href = `tel:${lead.phone}`;
                    phoneLink.textContent = lead.phone;
                    
                    // Update register time
                    const registerTimeSpan = newRow.querySelector('.bi-clock').closest('.badge');
                    const registerTimeText = registerTimeSpan.childNodes[registerTimeSpan.childNodes.length - 1];
                    registerTimeText.textContent = formatDate(lead.register_time);
                        
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
                    updateAssignedAdName(newRow, lead);
                    
                    // Update status select
                    updateAssignedSelectStatus(newRow, lead);
                    
                    // Update task list buttons
                    updateAssignedTaskList(newRow, lead);
                    
                    assignedTbody.appendChild(newRow);
                });

                // Update pagination
                updatePagination(assignedList, json.total_count, parseInt(page), 10, pageArgs);

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
});