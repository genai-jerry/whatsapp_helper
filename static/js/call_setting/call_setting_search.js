document.addEventListener('DOMContentLoaded', function() {
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
    $('#assigned_leads_search').unbind().keyup(handleAssignedOpportunitySearch);
});