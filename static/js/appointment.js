var currentPage = 1;
var max_setting = 0;
var current_max_setting = 0;
function updateOpportunityStatus(opportunityId, status, statusType, appointment_id) {
    // Make an AJAX request to update the opportunity status
    console.log('Updating appointment status:', appointment_id, status, statusType)
    $.ajax({
        url: '/appointment/status/'+opportunityId+"/"+appointment_id,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            status: status
        }),
        success: function(response) {
            loadAppointments(current_max_setting);
        },
        error: function(xhr, status, error) {
            // Handle the error response
            console.error('Error updating opportunity status:', error);
        }
    });
}

// Add click event to cancel button
function cancelAppointment(appointmentId) {
    // Ask for confirmation before canceling the appointment
    if (confirm("Are you sure you want to cancel this appointment?")) {
        // Call the cancel appointment API
        url = "/appointment/"+ appointmentId + "/cancel"
        $.post(url, 
            function(response) {
                if (response.status == "success") {
                    // Reload the appointments list
                    loadAppointments(current_max_setting);
                } else {
                    // Show an error message
                    alert('Failed to cancel appointment. Please try again.');
                }
            });
    }
}
function confirmAppointment(appointmentId) {
    // Call the confirm appointment API
    url = "/appointment/"+ appointmentId + "/confirm";
    $.post(url, 
    function(response) {
        if (response.status == "success") {
            // Reload the appointments list
            loadAppointments(current_max_setting);
        } else {
            // Show an error message
            alert('Failed to confirm appointment. Please try again.');
        }
    });
}

function loadAppointments(max, date) {
    if(max == -1){
        max = max_setting;
        current_max_setting = max_setting;
        max_setting = max_setting === 0 ? 1 : 0;
        currentPage = 1;
    }
    url = '/appointment/list?';

    if (date) {
        dateVal = getDateForDaysFromCurrentDate(date);
        dateVal = dateVal.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
        url += 'date=' + dateVal;
        max = 0;
        max_setting = 0;
    }
    url+='&max=' + max + '&page=' + currentPage;

    $.get(url, function(data) {
        if(date){
            resetListItem();
            setActiveListItem(date)
        }
        // Clear the current list of appointments
        $('#appointmentsTable tbody').empty();

        // Group appointments by appointment time
        var groupedAppointments = {};
        $.each(data.appointments, function(i, appointment) {
            var date = new Date(appointment.appointment_time);
            var formattedDate = date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });

            if (!groupedAppointments[formattedDate]) {
                groupedAppointments[formattedDate] = [];
            }

            groupedAppointments[formattedDate].push(appointment);
        });

        // Add the grouped appointments to the table
        $.each(groupedAppointments, function(dt, appointments) {
            var date = new Date(dt);
            var formattedDate = date.toLocaleString('en-IN', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });
            var dateRow = $('<tr><td colspan="6">' + formattedDate + '</td></tr>');
            $('#appointmentsTable tbody').append(dateRow);

            $.each(appointments, function(i, appointment) {
                var date = new Date(appointment.appointment_time);
                var url = appointment.opportunity_id ? '/opportunity/' + appointment.opportunity_id : '#'
                var telephone = appointment.applicant_telephone? appointment.applicant_telephone: telephone;
                var opportunityStatusSelect = createDataDropdown(appointment.opportunity_id, appointment.opportunity_status, data.opportunity_statuses, 'name', 'color_code', 'text_color', 'opportunity_status', 'Not Set', appointment.id);
                var formattedDate = date.toLocaleString('en-IN', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });
                var row = $(
                    '<tr class="grade-' + appointment.grade + '">' +
                    '<td></td>' +
                    '<td>' + (appointment.applicant_name ? '<a style="color: #c8cdd5" href="' + url + '">' +
                        appointment.applicant_name + '</a>' : appointment.opportunity_name) + 
                    addLinkToAppointment(appointment) +
                    '</td>' +
                    '<td><ul class="list-inline mb-1"><li class="list-inline-item mb-1"><span><a type="button" class="btn btn-success" href="tel:' + telephone + '"><i class="bi bi-telephone"></i>' + 
                                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-telephone" viewBox="0 0 16 16">' 
                                    +'<path d="M3.654 1.328a.678.678 0 0 0-1.015-.063L1.605 2.3c-.483.484-.661 1.169-.45 1.77a17.6 17.6 0 0 0 4.168 6.608 17.6 17.6 0 0 0 6.608 4.168c.601.211 1.286.033 1.77-.45l1.034-1.034a.678.678 0 0 0-.063-1.015l-2.307-1.794a.68.68 0 0 0-.58-.122l-2.19.547a1.75 1.75 0 0 1-1.657-.459L5.482 8.062a1.75 1.75 0 0 1-.46-1.657l.548-2.19a.68.68 0 0 0-.122-.58zM1.884.511a1.745 1.745 0 0 1 2.612.163L6.29 2.98c.329.423.445.974.315 1.494l-.547 2.19a.68.68 0 0 0 .178.643l2.457 2.457a.68.68 0 0 0 .644.178l2.189-.547a1.75 1.75 0 0 1 1.494.315l2.306 1.794c.829.645.905 1.87.163 2.611l-1.034 1.034c-.74.74-1.846 1.065-2.877.702a18.6 18.6 0 0 1-7.01-4.42 18.6 18.6 0 0 1-4.42-7.009c-.362-1.03-.037-2.137.703-2.877z"/>' 
                                +'</svg>' +
                            '</span></a></li><li class="list-inline-item mb-1"><span>' +
                                '<a type="button" class="btn btn-success" target="WhatsApp" href="https://wa.me/' + telephone + '"><i class="bi bi-whatsapp"></i>' +
                                '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-whatsapp" viewBox="0 0 16 16">' +
                            '<path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>' +
                            '</svg></a></span></li></ul></td>'+
                    '<td style="color: #c8cdd5">' + appointment.mentor_name + '</td>' +
                    '<td style="color: #c8cdd5">' + formattedDate + (appointment.conflicted ? ' <i class="bi bi-exclamation-triangle-fill" style="color: blue;"></i><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="blue" class="bi bi-exclamation-triangle-fill" viewBox="0 0 16 16">' +
                    '<path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5m.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2"/>'+
                    '</svg>' : '') + '</td>' +
                    '<td><button class="btn btn-info btn-sm expand mb-2">See Details</button>' +
                    '<button id="canceled" class="btn btn-danger btn-sm mb-2" onclick="cancelAppointment('+ appointment.id +')">Mark as Canceled</button>' +
                    (appointment.confirmed ? '' : '<button id="confirmed" class="btn btn-success btn-sm mb-2" onclick="confirmAppointment(' + appointment.id + ')">Confirm</button>')  +
                    '</td>' +
                    '<td style="color: #c8cdd5">' + opportunityStatusSelect + '</td>' +
                    '<td>' + task_comment_actions(appointment.opportunity_id, appointment.opportunity_name, appointment.task_count, appointment.comment_count, true) + '</td>' +
                    '</tr>'
                );

                var details = $(
                    '<tr class="details" style="display: none;">' +
                    '<td colspan="5">' +
                    '<strong>Career Challenge:</strong> ' + appointment.career_challenge + '<br>' +
                    '<strong>Challenge Description:</strong> ' + appointment.challenge_description + '<br>' +
                    '<strong>Urgency:</strong> ' + appointment.urgency + '<br>' +
                    '<strong>Salary Range:</strong> ' + appointment.salary_range + '<br>' +
                    '<strong>Expected Salary:</strong> ' + appointment.expected_salary + '<br>' +
                    '<strong>Current Employer:</strong> ' + appointment.current_employer + '<br>' +
                    '<strong>Financial Situation:</strong> ' + appointment.financial_situation +'<br>' +
                    '<strong>Whatsapp Number:</strong> ' + appointment.appointment_number +
                    
                    '</td>' +
                    '</tr>'
                );

                $('#appointmentsTable tbody').append(row, details);
            });
        });
        // Set the view setting based on max_setting value
        var viewSetting = current_max_setting === 0 ? 'View All' : 'View Pending';
        // Update the view setting element
        $('#view_setting').text(viewSetting);
        // Update the pagination info
        $('#page-info').text('Page ' + data.page + ' of ' + data.total_pages);

        // Add click event to expand buttons
        $('.expand').click(function() {
            $(this).closest('tr').next('.details').toggle();
        });           
    });
}
function addLinkToAppointment(appointment){
    if(appointment.opportunity_id == null){
        return '&nbsp;<span style="cursor: pointer;" id="link-icon-' + appointment.id + '" class="link-icon" onclick="showLinkTextBox(' + appointment.id + ',' + appointment.opportunity_id + ')">' +
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" class="bi bi-link-45deg" viewBox="0 0 16 16">' +
            '<path d="M4.715 6.542 3.343 7.914a3 3 0 1 0 4.243 4.243l1.828-1.829A3 3 0 0 0 8.586 5.5L8 6.086a1 1 0 0 0-.154.199 2 2 0 0 1 .861 3.337L6.88 11.45a2 2 0 1 1-2.83-2.83l.793-.792a4 4 0 0 1-.128-1.287z"/>' +
            '<path d="M6.586 4.672A3 3 0 0 0 7.414 9.5l.775-.776a2 2 0 0 1-.896-3.346L9.12 3.55a2 2 0 1 1 2.83 2.83l-.793.792c.112.42.155.855.128 1.287l1.372-1.372a3 3 0 1 0-4.243-4.243z"/>' +
            '</svg></span>'
    }
    return '';
}

function handleCalendarSelect(date){
    loadAppointments(-1, date);
}

// Add this function to handle showing the text box
function showLinkTextBox(appointmentId) {
    const textBox = $('<div class="input-group mb-3">' +
        '<form action="/appointment/' + appointmentId + '/link" method="POST">' +
        '<input type="text" class="form-control" placeholder="Enter Opportunity Id" name="opportunity_id" id="link-input-' + appointmentId + '">' +
        '<div class="input-group-append">' +
        '<button class="btn btn-primary" type="submit">Link</button>' +
        '</div>' +
        '</form>' +
        '</div>');
    $('#link-icon-' + appointmentId).replaceWith(textBox);
}

function saveLink(appointmentId) {
    const linkUrl = $('#link-input-' + appointmentId).val();
    // Here you can add AJAX call to save the link
    console.log('Saving link:', linkUrl, 'for appointment:', appointmentId);
    // After saving, reload the appointments or update the UI
    loadAppointments(current_max_setting);
}

$(document).ready(function() {
    loadAppointments(-1);

    $('#prev').click(function() {
        if (currentPage > 1) {
            currentPage--;
            loadAppointments(current_max_setting);
        }
    });

    $('#next').click(function() {
        currentPage++;
        loadAppointments(current_max_setting);
    });
});
