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
        
        const pipelineList = this.closest('.pipeline-list');
        const type = pipelineList ? pipelineList.id : '';
        const pipelineTbody = pipelineList ? pipelineList.querySelector('tbody') : null;
        const cardBody = pipelineList.closest('.card-body');
        
        const page = this.getAttribute('data-page');
        const pageArgs = this.getAttribute('data-page-args');
        const selectedEmployeeId = this.getAttribute('data-selected-employee-id');
        
        const templateRow = $('.pipeline-item')[0];
        
        const params = new URLSearchParams();
        params.append('type', type);
        params.append(pageArgs, page);
        if (selectedEmployeeId) {
            params.append('selected_employee_id', selectedEmployeeId);
        }
        
        // Add loading effect
        cardBody.classList.add('loading-blur');
        
        fetch(`/review/call-setting?${params.toString()}`, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(json => {
            if (pipelineTbody) {
                pipelineTbody.innerHTML = '';
                
                json.items.forEach(lead => {
                    const newRow = templateRow.cloneNode(true);
                    
                    const opportunityLink = newRow.querySelector('a[href^="/opportunity/"]');
                    opportunityLink.href = `/opportunity/${lead.id}`;
                    opportunityLink.title = lead.name;
                    opportunityLink.textContent = lead.name.length > 15 ? lead.name.substring(0, 15) + '...' : lead.name;
                    
                    const registerTimeSpan = newRow.querySelectorAll('.register-time')[0];
                    registerTimeSpan.lastChild.textContent = new Date(lead.register_time).toLocaleDateString();
                    
                    const adNameP = newRow.querySelector('.bi-megaphone')?.closest('p');
                    if (adNameP) {
                        if (lead.ad_name) {
                            const adNameSpan = adNameP.querySelector('.badge');
                            adNameSpan.title = lead.ad_name;
                            adNameSpan.lastChild.textContent = 
                                lead.ad_name.length > 10 ? lead.ad_name.substring(0, 10) + '...' : lead.ad_name;
                        } else {
                            adNameP.remove();
                        }
                    }
                    
                    pipelineTbody.appendChild(newRow);
                });
                // Update data-opportunity-id for assign buttons
                pipelineTbody.querySelectorAll('.assign-btn').forEach(btn => {
                    btn.setAttribute('data-opportunity-id', json.items[0].id);
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
            }, 300); // Small delay to ensure smooth transition
        });
    }
    
    // Add initial event listeners
    $('.page-link').each(function() {
        $(this).unbind().click(handlePageClick);
    });
});