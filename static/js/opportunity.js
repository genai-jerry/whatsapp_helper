
var page = 1;
var totalPages = 1;

function updateOpportunityStatus(opportunityId, status, statusType, context_id) {
    // Make an AJAX request to update the opportunity status
    console.log('Updating opportunity status:', opportunityId, status, statusType)
    $.ajax({
        url: '/opportunity/status/'+opportunityId+"/"+statusType,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            status: status
        }),
        success: function(response) {
            loadOpportunities($('#searchTerm').val(), $('#searchType').val(), filters);
        },
        error: function(xhr, status, error) {
            // Handle the error response
            console.error('Error updating opportunity status:', error);
        }
    });
}

function loadOpportunities(searchTerm, searchType, filters) {
    
    var url = '/opportunity/list?page=' + page;
    if (searchTerm && searchType) {
        url += '&searchTerm=' + encodeURIComponent(searchTerm) + '&searchType=' + encodeURIComponent(searchType);
    }
    if (filters) {
        var filterTypes = Object.keys(filters).map(function(fType) {
            return filters[fType].type;
        }).join(',');

        var filterValues = Object.keys(filters).map(function(fType) {
            return filters[fType].value;
        }).join(',');

        url += '&filterType=' + encodeURIComponent(filterTypes) + '&filterValue=' + encodeURIComponent(filterValues);
    }
    $.getJSON(url, function(data) {
        // Clear the current list of opportunities
        $('#opportunitiesTable tbody').empty();

        // Add the new opportunities to the list
        data.items.forEach(function(opportunity, index) {
            var date = new Date(opportunity.date);
            var callStatusSelect = createDataDropdown(opportunity.id, opportunity.call_status, data.call_statuses, 'name', 'color_code', 'text_color', 'call_status', 'Not Set');
            var opportunityStatusSelect = createDataDropdown(opportunity.id, opportunity.opportunity_status, data.opportunity_statuses, 'name', 'color_code', 'text_color', 'opportunity_status', 'Not Set');
            var agentSelect = createDataDropdown(opportunity.id, opportunity.agent, data.sales_agents, 'name', 'color_code', 'text_color', 'agent', 'Not Set');
            var formattedDate = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Kolkata' })).toLocaleString('en-IN', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
            var row = '<tr>' +
                '<td><a href="./' + opportunity.id + '">' + opportunity.name + '</a><br>' + opportunity.phone + '<br>' 
                    + opportunity.email + '</td>' +
                '<td>' + formattedDate + '</td>' +
                '<td><ul class="list-inline mb-1"><li class="list-inline-item mb-1"><span><a type="button" class="btn btn-success" href="tel:' + opportunity.phone + '"><i class="bi bi-telephone"></i>' + 
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-telephone" viewBox="0 0 16 16">' 
                            +'<path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.6 17.6 0 0 0 4.168 6.608 17.6 17.6 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.68.68 0 0 0-.58-.122l-2.19.547a1.75 1.75 0 0 1-1.657-.459L5.482 8.062a1.75 1.75 0 0 1-.46-1.657l.548-2.19a.68.68 0 0 0-.122-.58zM1.884.511a1.745 1.745 0 0 1 2.612.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.68.68 0 0 0 .178.643l2.457 2.457a.68.68 0 0 0 .644.178l2.189-.547a1.75 1.75 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.6 18.6 0 0 1-7.01-4.42 18.6 18.6 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877z"/>' 
                        +'</svg>' +
                    '</span></a></li><li class="list-inline-item mb-1"><span>' +
                        '<a type="button" class="btn btn-success" target="WhatsApp" href="https://wa.me/' + opportunity.phone + '"><i class="bi bi-whatsapp"></i>' +
                        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-whatsapp" viewBox="0 0 16 16">' +
                    '<path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>' +
                    '</svg></a></span></li></ul></td>'+
                '<td>' + (opportunity.ad_name ? '<b>Name:</b> '+opportunity.ad_name : 'Not Available')+'<br>' +
                    (opportunity.ad_placement ? '<b>Placement:</b> '+opportunity.ad_placement : '')+'<br>' +
                        (opportunity.ad_medium ? '<b>Medium:</b> '+opportunity.ad_medium : '')+'</td>' +
                '<td>' + callStatusSelect
                    if (opportunity.video_watched) {
                        row += '</br><i class="bi bi-camera-video"></i>' 
                        row += '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="blue" class="bi bi-camera-video" viewBox="0 0 16 16">' +
                            '<path fill-rule="evenodd" d="M0 5a2 2 0 0 1 2-2h7.5a2 2 0 0 1 1.983 1.738l3.11-1.382A1 1 0 0 1 16 4.269v7.462a1 1 0 0 1-1.406.913l-3.111-1.382A2 2 0 0 1 9.5 13H2a2 2 0 0 1-2-2zm11.5 5.175 3.5 1.556V4.269l-3.5 1.556zM2 4a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h7.5a1 1 0 0 0 1-1V5a1 1 0 0 0-1-1z"/>' +
                            '</svg>';
                    }

                row += '</td>' +
                '<td>' + (opportunity.opportunity_status ? opportunity.opportunity_status : 'Not Set') + '</td>' +
                '<td>' + agentSelect + '</td>' +
                '<td>' + task_comment_actions(opportunity.id, opportunity.name, opportunity.task_count, opportunity.comment_count) + '</td>' +
                '</tr>';
            $('#opportunitiesTable tbody').append(row);
        });

        // Update the pagination info
        $('#page-info').text('Page ' + data.page + ' of ' + data.total_pages);
        totalPages = data.total_pages;
        // Load the initial data
        $.getJSON('/opportunity/call_status', function(data) {
            var callStatusFilter = createFilterDropdown(null, filters && filters.hasOwnProperty('cs.id') ? filters['cs.id'].name : null, data, 
                'name', 'color_code', 'text_color', 'cs.id', 'Call Status');
            $('#call_status_heading').empty();
            $('#call_status_heading').append(callStatusFilter);
        });
        $.getJSON('/opportunity/opportunity_status', function(data) {
            var opportunityStatusFilter = createFilterDropdown(null, filters && filters.hasOwnProperty("os.id") ? filters['os.id'].name: null, data, 
                'name', 'color_code', 'text_color', 'os.id', 'Opportunity Status');
            $('#opportunity_status_heading').empty();
            $('#opportunity_status_heading').append(opportunityStatusFilter);
        });
        $.getJSON('/opportunity/sales_agents', function(data) {
            var opportunityStatusFilter = createFilterDropdown(null, filters && filters.hasOwnProperty("sa.id") ? filters['sa.id'].name: null, data, 
                'name', 'color_code', 'text_color', 'sa.id', 'Optin Caller');
            $('#agent_heading').empty();
            $('#agent_heading').append(opportunityStatusFilter);
        });
    });
}
class Filter {
    constructor(type, value, name) {
        this.type = type;
        this.value = value;
        this.name = name;
    }
}

var filters = {};

function filterOpportunity(fType, fValue, fName) {
    var searchTerm = $('#searchTerm').val();
    var searchType = $('#searchType').val();
    var filter = new Filter(fType, fValue, fName);
    filters[fType] = filter;
    loadOpportunities(searchTerm, searchType, filters);
}

$(document).ready(function() {
    
    // Load the first page of opportunities
    var searchTerm = $('#searchTerm').val();
    var searchType = $('#searchType').val();
    loadOpportunities(searchTerm, searchType);

    // Initialize the flatpickr calendar
    flatpickr("#opp_registered_date", {
        dateFormat: "Y-m-d",
        onClose: function(selectedDates, dateStr, instance) {
            var searchTerm = $('#searchTerm').val();
            var searchType = $('#searchType').val();
            page = 1;  // Reset to the first page
            filterType = "DATE(o.last_register_time)";
            filterValue = dateStr;
            var filter = new Filter(filterType, filterValue, 'Date');
            filters[filterType] = filter;
            loadOpportunities(searchTerm, searchType, filters);
        },
        disableMobile: true // Add this line to disable the dropdown on mobile
    });

    // Handle the Previous button click
    $('#prev').click(function() {
        if (page > 1) {
            page--;
            var searchTerm = $('#searchTerm').val();
            var searchType = $('#searchType').val();
            loadOpportunities(searchTerm, searchType, filters);
        }
    });
    // Handle the search form submission
    $('#searchForm').submit(function(event) {
        event.preventDefault();
        var searchTerm = $('#searchTerm').val();
        var searchType = $('#searchType').val();
        page = 1;  // Reset to the first page
        loadOpportunities(searchTerm, searchType, filters);
    });
    
    // Handle the Next button click
    $('#next').click(function() {
        if (page < totalPages) {
            page++;
            var searchTerm = $('#searchTerm').val();
            var searchType = $('#searchType').val();
            loadOpportunities(searchTerm, searchType, filters);
        }
    });
    // Handle the First button click
    $('#first').click(function() {
        if (page !== 1) {
            page = 1;
            var searchTerm = $('#searchTerm').val();
            var searchType = $('#searchType').val();
            loadOpportunities(searchTerm, searchType, filters);
        }
    });
});