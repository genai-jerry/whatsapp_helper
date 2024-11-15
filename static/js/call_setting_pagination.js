document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get the closest pipeline-list parent to identify the type
            const pipelineList = this.closest('.pipeline-list');
            const type = pipelineList ? pipelineList.id : '';
            const pipelineTbody = pipelineList ? pipelineList.querySelector('tbody') : null;
            
            // Get pagination data from clicked element
            const page = this.getAttribute('data-page');
            const pageArgs = this.getAttribute('data-page-args');
            const selectedEmployeeId = this.getAttribute('data-selected-employee-id');
            
            // Get template row for cloning
            const templateRow = $('.pipeline-item')[0];
            
            // Prepare the query parameters
            const params = new URLSearchParams();
            params.append('type', type);
            params.append(pageArgs, page);
            if (selectedEmployeeId) {
                params.append('selected_employee_id', selectedEmployeeId);
            }
            
            // Make the AJAX call
            fetch(`/review/call-setting?${params.toString()}`, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(json => {
                if (pipelineTbody) {
                    // Clear existing rows
                    pipelineTbody.innerHTML = '';
                    
                    json.forEach(lead => {
                        // Clone the template row
                        const newRow = templateRow.cloneNode(true);
                        
                        // Update link attributes and text
                        const opportunityLink = newRow.querySelector('a[href^="/opportunity/"]');
                        opportunityLink.href = `/opportunity/${lead.id}`;
                        opportunityLink.title = lead.name;
                        opportunityLink.textContent = lead.name.length > 15 ? lead.name.substring(0, 15) + '...' : lead.name;
                        
                        
                        // Update register time
                        const registerTimeSpan = newRow.querySelector('.bi-clock').closest('.badge');
                        registerTimeSpan.lastChild.textContent = new Date(lead.register_time).toLocaleDateString();
                        
                        // Update last updated time if exists
                        const lastUpdatedP = newRow.querySelector('.bi-telephone-outbound')?.closest('p');
                        if (lastUpdatedP) {
                            if (lead.last_updated) {
                                lastUpdatedP.querySelector('.badge').lastChild.textContent = 
                                    new Date(lead.last_updated).toLocaleDateString();
                            } else {
                                lastUpdatedP.remove();
                            }
                        }
                        
                        // Update ad name if exists
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
                        
                        // Append the new row
                        pipelineTbody.appendChild(newRow);
                    });

                    // Reinitialize tooltips
                    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                        return new bootstrap.Tooltip(tooltipTriggerEl)
                    });
                }
            })
            .catch(error => {
                console.error('Error fetching pagination data:', error);
            });
        });
    });
});