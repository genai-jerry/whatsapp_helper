class CallSettingPagination {
    constructor() {
        this.pipelineApptElements = {};
        this.assignedApptElements = {};
        
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

        // Initialize event listeners
        this.initializeEventListeners();
    }

    updatePagination(paginationNav, totalCount, currentPage, pageSize, pageArgs) {
        if (!paginationNav) return;
        const totalPages = Math.ceil(totalCount / pageSize);
        if (totalPages <= 1) {
            $(paginationNav).hide();
            return;
        }
        $(paginationNav).show();
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

        // Add ellipsis and other pages logic
        if (currentPage > 3) {
            const ellipsis1 = document.createElement('li');
            ellipsis1.className = 'page-item disabled';
            ellipsis1.innerHTML = `<span class="page-link">...</span>`;
            ul.appendChild(ellipsis1);
        }

        if (currentPage != 1 && currentPage != totalPages) {
            const currentLi = document.createElement('li');
            currentLi.className = 'page-item active';
            currentLi.innerHTML = `
                <a data-page-args="${pageArgs}" 
                   data-page="${currentPage}"
                   class="page-link" 
                   href="#">${currentPage}</a>`;
            ul.appendChild(currentLi);
        }

        if (currentPage < totalPages - 2) {
            const ellipsis2 = document.createElement('li');
            ellipsis2.className = 'page-item disabled';
            ellipsis2.innerHTML = `<span class="page-link">...</span>`;
            ul.appendChild(ellipsis2);
        }

        // Last page
        if (totalPages > 1) {
            const lastLi = document.createElement('li');
            lastLi.className = `page-item ${currentPage == totalPages ? 'active' : ''}`;
            lastLi.innerHTML = `
                <a data-page-args="${pageArgs}" 
                   data-page="${totalPages}"
                   class="page-link" 
                   href="#">${totalPages}</a>`;
            ul.appendChild(lastLi);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${currentPage == totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `
            <a data-page-args="${pageArgs}" 
               data-page="${currentPage+1}"
               class="page-link" 
               href="#"
               ${currentPage == totalPages ? 'tabindex="-1" aria-disabled="true"' : ''}>
                Next
            </a>`;
        ul.appendChild(nextLi);

        // Reattach click handlers
        ul.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', this.handlePageClick.bind(this));
        });
    }

    handlePageClick(e) {
        e.preventDefault();
        const leadsList = e.target.closest('.leads-list');
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
        const element_id = leadsList.id;
        const page = e.target.getAttribute('data-page');
        const pageArgs = e.target.getAttribute('data-page-args');
        const params = {};
        params[pageArgs] = page;
        if (isPipeline) {
            window.leadPipeline.handlePipeline(element_id, params).then(([totalCount, card]) => {
                this.handleResponse(card, page, pageArgs, totalCount);
            });
        }
        if (isAssigned) {
            window.assignedLead.handleAssigned(element_id, params).then(([totalCount, card]) => {
                this.handleResponse(card, page, pageArgs, totalCount);
            });
        }
        if (isAssignedAppointment) {
            window.assignedAppointment.handleAppointment(element_id, params).then(([totalCount, card]) => {
                this.handleResponse(card, page, pageArgs, totalCount);
            });
        }
        if (isPipelineAppointment) {
            window.leadAppointment.handleAppointment(element_id, params).then(([totalCount, card]) => {
                this.handleResponse(card, page, pageArgs, totalCount);
            });
        }
    }

    handleResponse(card, page, pageArgs, totalCount) {
        const pageNav = $(card).find('nav[aria-label="pagination"]')[0];
        // Update pagination
        if (pageNav) {
            this.updatePagination(pageNav, totalCount, parseInt(page), 10, pageArgs);
        }
    }

    initializeEventListeners() {
        $('.page-link').each((index, element) => {
            $(element).unbind().click(this.handlePageClick.bind(this));
        });
    }
}

// Initialize the pagination functionality
window.paginationInitialized = false;
document.addEventListener('DOMContentLoaded', () => {
    if (!window.paginationInitialized) {
        window.callSettingPagination = new CallSettingPagination();
        window.paginationInitialized = true;
    }
}); 