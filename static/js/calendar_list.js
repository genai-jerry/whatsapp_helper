var currentDate = null;
function advAppointments(page, direction) {
    // Logic to handle previous button click
    if (currentDate === null) {
        currentDate = new Date();
    }
    if (direction === 'prev') {
        // Subtract 7 days from the current date
        var previousDate = new Date(currentDate.getTime() - (7 * 24 * 60 * 60 * 1000));
        currentDate = previousDate;
    } else {
        // Add 7 days to the current date
        var nextDate = new Date(currentDate.getTime() + (7 * 24 * 60 * 60 * 1000));
        currentDate = nextDate;
    }
    

    for (var i = 0; i < 7; i++) {
        var date = getDateForDaysFromCurrentDate(i);
        $('#date-' + i).text(formatDate(date));
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