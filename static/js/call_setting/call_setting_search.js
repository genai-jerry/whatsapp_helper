class LeadsSearch{
    constructor(){
        this.initialize();
    }

    initialize(){
        $('#assigned_leads_search').unbind().keyup(this.handleAssignedOpportunitySearch);
    }
    async handleAssignedOpportunitySearch(searchInput){
        console.log(searchInput);
        const searchValue = $('#assigned_leads_search').val();
        console.log(searchValue);
        // Define the sections and their parameters
        const sections = [
            {
                containerId: 'assigned_appointments',
                pageArgs: 'assigned_appt_page',
                type: 'appointments'
            },
            {
                containerId: 'assigned_leads',
                pageArgs: 'assigned_leads_page',
                type: 'leads'
            },
            {
                containerId: 'assigned_follow_up',
                pageArgs: 'assigned_follow_up_page',
                type: 'leads'
            },
            {
                containerId: 'assigned_no_show',
                pageArgs: 'assigned_no_show_page',
                type: 'leads'
            }
        ];
        
        
        // Process each section
        sections.forEach(section => {
            // Create Search Params
            const params = {};
            params[section.pageArgs] = '1';
            params['search'] = searchValue;
            params['type'] = section.containerId;
            const cardBody = $(`#${section.containerId}`)[0];
            const pageNav = $(cardBody).find('nav[aria-label="pagination"]')[0];
            // if container is a list then get first element
            if (section.type == 'leads') {
                window.assignedLead.handleAssigned(section.containerId, params).then(([totalCount, card]) => {
                    window.callSettingPagination.handleResponse(card, '1', section.pageArgs, totalCount);
                });
            } else {
                window.assignedAppointment.handleAppointment(section.containerId, params).then(([totalCount, card]) => {
                    window.callSettingPagination.handleResponse(card, '1', section.pageArgs, totalCount);
                });  
            }       
        });
    }
}    

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.leadsSearch = new LeadsSearch();
});