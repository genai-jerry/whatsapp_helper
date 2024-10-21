var currentDate = null;
function next(calendar_type) {
    // Logic to handle previous button click
    if (currentDate === null) {
        currentDate = new Date();
    }
        // Add 7 days to the current date
    var nextDate = new Date(currentDate.getTime() + (7 * 24 * 60 * 60 * 1000));
    if (calendar_type == 'monthly') {
        nextDate = new Date(currentDate.getFullYear() + 1, currentDate.getMonth(), 1);
    }
    currentDate = nextDate;
    
    redrawDates(calendar_type);
}
function prev(calendar_type) {
    // Logic to handle previous button click
    if (currentDate === null) {
        currentDate = new Date();
    }
    var previousDate = new Date(currentDate.getTime() - (7 * 24 * 60 * 60 * 1000));
    if (calendar_type == 'monthly') {
        previousDate = new Date(currentDate.getFullYear(), currentDate.getMonth()-1  , 1);
    }
    currentDate = previousDate;

    redrawDates(calendar_type);
}

function redrawDates(calendar_type) {
    // Logic to redraw the dates
    if (calendar_type === 'weekly') {
        for (var i = 0; i < 7; i++) {
            var date = getDateForDaysFromCurrentDate(i);
            $('#date-' + i).text(formatDate(date));
        }
    } else if (calendar_type === 'monthly') {
        for (var i = 0; i < 12; i++) {
            var date = new Date(currentDate.getFullYear(), currentDate.getMonth() + i, 1);
            var formattedMonthYear = date.toLocaleString('default', { month: 'long' }) + ' ' + date.getFullYear();
            $('#date-' + i).text(formattedMonthYear);
        }
    }
    resetListItem();
}

function getDateForDaysFromCurrentDate(i){
    if (currentDate === null) {
        currentDate = new Date();
    }
    var date = new Date(currentDate.getTime() + (i * 24 * 60 * 60 * 1000));
    return date;
}

function setActiveListItem(value) {
    // Add active class and white-text to the li element with id data-{value}
    $('#li-'+value).addClass('selected-date');
    $('#li-'+value).removeClass('normal-date');
}

function resetListItem() {
    // Remove active class and white-text from all li elements
    for (var i = 0; i <= 6; i++) {
        $('#li-'+i).removeClass('selected-date');
        $('#li-'+i).addClass('normal-date');
    }
}

let selectedMonth = null;
let selectedYear = null;

// Add this new function to parse URL parameters
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// Add this function to initialize the calendar based on URL parameters
function initializeCalendarFromUrl() {
    var monthParam = getUrlParameter('month');

    if (monthParam) {
        var [month, year] = monthParam.split(' ');
        selectedMonth = month;
        selectedYear = year;
    }else{
        selectedMonth = new Date().toLocaleString('default', { month: 'long' });
        selectedYear = new Date().getFullYear();
    }
}

// Call this function when the page loads
$(document).ready(function() {
    initializeCalendarFromUrl();
});
