function fetchAndDisplayMetrics(startDate, endDate, tableBody) {
    $.ajax({
        url: `/dashboard/metrics?start_date=${startDate}&end_date=${endDate}`,
        type: 'GET',
        dataType: 'json',
        beforeSend: function() {
            // Show loading feedback
            tableBody.html('<tr><td colspan="2">Loading...</td></tr>');
        },
        success: function(data) {
            // Clear table body
            tableBody.html('');
            report = JSON.parse(data);
            // Insert a new row for each metric
            
            for (const [key, value] of Object.entries(report)) {
                const row = $('<tr></tr>');
                row.append($('<td></td>').text(key));
                row.append($('<td></td>').text(value[0]));
                row.append($('<td></td>').text(value[1] !== -1 ? value[1] + '%' : 'N/A'));
                tableBody.append(row);
            }
        },
        error: function() {
            // Show error feedback
            tableBody.html('<tr><td colspan="2">Error loading data</td></tr>');
        },
        complete: function() {
            // Hide loading feedback
            tableBody.find('tr:contains("Loading...")').remove();
        }
    });
}
function fetchAndDisplayReport(startDate, endDate, tableBody) {
    // Show loading feedback
    tableBody.html('<tr><td colspan="3">Loading...</td></tr>');
    
    $.ajax({
        url: `/dashboard/report?start_date=${startDate}&end_date=${endDate}`,
        method: 'GET',
        dataType: 'json',
        success: function(report) {
            tableBody.empty();  // clear previous table data
            report = JSON.parse(report);
            for (const data of report) {
                row = $('<tr></tr>');
                row.append($('<td></td>').text(data.name || 'Call Pending'));
                row.append($('<td></td>').text(data.count));
                row.append($('<td></td>').text(data.percentage));
                tableBody.append(row);
            }
        },
        error: function() {
            // Show error feedback
            tableBody.html('<tr><td colspan="3">Error loading data</td></tr>');
        },
        complete: function() {
            // Hide loading feedback
            tableBody.find('tr:contains("Loading...")').remove();
        }
    });
}

function formatDate(date) {
    year = date.getFullYear();
    month = String(date.getMonth() + 1).padStart(2, '0');
    day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

$('#generate_report').click(function() {
    startDate = $('#start_date').val();
    endDate = $('#end_date').val();
    tableBody = $('#customReportTable').find('tbody');

    fetchAndDisplayReport(startDate, endDate, tableBody);
    fetchAndDisplayMetrics(startDate, endDate, $('#periodicMetrics').find('tbody'));
});
