function loadSalesProjection() {
    const employeeId = document.getElementById('employee').value;
    const month = selectedMonth;
    const year = selectedYear;

    if (!employeeId) {
        return;
    }

    // Show loading modal
    $('#loadingModal').modal('show');

    $.ajax({
        url: '/metrics/get_sales_projection',
        type: 'GET',
        data: {
            sales_agent_id: employeeId,
            month: month,
            year: year
        },
        success: function(response) {
            // Hide loading modal
            $('#loadingModal').modal('hide');

            // Populate form fields with the received data
            if (response.projection) {
                document.getElementById('total_call_slots').value = response.projection.total_call_slots;
                document.getElementById('closure_percentage_goal').value = response.projection.closure_percentage_goal;
                document.getElementById('closure_percentage_projected').value = response.projection.closure_percentage_projected;
                document.getElementById('sales_value_projected').value = response.projection.sales_value_projected;
                document.getElementById('sales_value_goal').value = response.projection.sales_value_goal;
                // Add more fields as needed
            } else {
                // Clear form fields if no projection data is found
                document.getElementById('total_call_slots').value = '';
                document.getElementById('closure_percentage_goal').value = '';
                document.getElementById('closure_percentage_projected').value = '';
                document.getElementById('sales_value_projected').value = '';
                document.getElementById('sales_value_goal').value = '';
                // Clear more fields as needed
            }
        },
        error: function(xhr, status, error) {
            // Hide loading modal
            $('#loadingModal').modal('hide');
            
            console.error('Error fetching sales projection:', error);
            alert('An error occurred while fetching the sales projection. Please try again.');
        }
    });
}
