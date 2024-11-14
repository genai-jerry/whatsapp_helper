document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // Get the closest pipeline-list parent to identify the type
            const pipelineList = this.closest('.pipeline-list');
            const type = pipelineList ? pipelineList.id : '';
            
            // Get pagination data from clicked element
            const page = this.getAttribute('data-page');
            const pageArgs = this.getAttribute('data-page-args');
            const selectedEmployeeId = this.getAttribute('data-selected-employee-id');
            
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
            .then(response => response.text())
            .then(html => {
                // Replace the content of the pipeline list
                if (pipelineList) {
                    pipelineList.innerHTML = html;
                }
            })
            .catch(error => {
                console.error('Error fetching pagination data:', error);
            });
        });
    });
});