function setupDropdown(opportunity_id, selectedValue, options, nameKey, colorKey, textColorKey, status_type) {
    var dropdown = '<div class="btn-group">';
    var optionColor = getOptionColor(selectedValue, options, colorKey);
    var textColor = getOptionColor(selectedValue, options, textColorKey);
    dropdown += '<span id="status-' + status_type + '-'+ opportunity_id +'">';
    dropdown += '<button type="button" class="btn btn-secondary dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false" style="background-color: ' 
        + (optionColor ? optionColor : 'gray') + '; color: ' + (textColor ? textColor : 'black') + '">';
    dropdown += selectedValue ? selectedValue : status_type;
    dropdown += '</button>';
    dropdown += '<ul class="dropdown-menu">';
    return dropdown;
}
function createDataDropdown(opportunity_id, selectedValue, options, nameKey, colorKey, textColorKey, status_type, default_value, context_id) {
    var dropdown = setupDropdown(opportunity_id, selectedValue, options, nameKey, colorKey, textColorKey, default_value);
    options.forEach(function(option) {
        var selected = option[nameKey] === selectedValue ? 'active' : '';
        dropdown += '<li><a class="dropdown-item ' + selected + '" href="#" style="background-color: ' + option[colorKey] + '; color: ' + option[textColorKey] + '" onclick="updateOpportunityStatus(' + opportunity_id + ',\'' + option["id"] + '\',\'' + status_type + '\',\'' + context_id + '\')">' + option[nameKey] + '</a></li>';
        
    });
    dropdown += '</ul>';
    dropdown += '</div>';
    dropdown += '</span>';
    return dropdown;
}
function createFilterDropdown(opportunity_id, selectedValue, options, nameKey, colorKey, textColorKey, status_type, status_name) {
    var dropdown = setupDropdown(opportunity_id, selectedValue, options, nameKey, colorKey, textColorKey, status_name);
    options.forEach(function(option) {
        var selected = option[nameKey] === selectedValue ? 'active' : '';
        dropdown += '<li><a class="dropdown-item ' + selected + '" href="#" style="background-color: ' + option[colorKey] + '; color: ' + option[textColorKey] + '" onclick="filterOpportunity(\'' + status_type + '\',' + option["id"] + ',\'' + option[nameKey] + '\')">' + option[nameKey] + '</a></li>';
        
    });
    dropdown += '</ul>';
    dropdown += '</div>';
    dropdown += '</span>';
    return dropdown;
}

function formatDate(date) {
    var options = { weekday: 'short',day: 'numeric' , month: 'short'};
    return date.toLocaleDateString(undefined, options);
}


function getOptionColor(selectedValue, options, colorKey) {
    var selectedOption = options.find(function(option) {
        return option.name === selectedValue;
    });
    return selectedOption ? selectedOption[colorKey] : null;
}

function task_comment_actions(opportunity_id, opportunity_name){
    let icons = '<div class="btn-group" role="group" aria-label="Task and Comment Actions">' +
                    '  <a type="button" class="btn btn-primary btn-sm task-comment-btn border border-white" onclick="listTasks(' + opportunity_id + ', \'' + opportunity_name  + '\')">' +
                    '    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-list-task" viewBox="0 0 16 16">' +
                    '      <path fill-rule="evenodd" d="M2 2.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5V3a.5.5 0 0 0-.5-.5H2zM3 3H2v1h1V3z"/>' +
                    '      <path d="M5 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM5.5 7a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1h-9zm0 4a.5.5 0 0 0 0 1h9a.5.5 0 0 0 0-1h-9z"/>' +
                    '      <path fill-rule="evenodd" d="M1.5 7a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5v1a.5.5 0 0 1-.5.5H2a.5.5 0 0 1-.5-.5V7zM2 7h1v1H2V7zm0 3.5a.5.5 0 0 0-.5.5v1a.5.5 0 0 0 .5.5h1a.5.5 0 0 0 .5-.5v-1a.5.5 0 0 0-.5-.5H2zm1 .5H2v1h1v-1z"/>' +
                    '    </svg>' +
                    '  </a>' +
                    '  <button type="button" class="btn btn-primary btn-sm task-comment-btn border border-white" onclick="showCreateTaskModal(' + opportunity_id + ', \'' + opportunity_name + '\')">' +
                    '    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-plus-square" viewBox="0 0 16 16">' +
                    '      <path d="M14 1a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>' +
                    '      <path d="M8 4a.5.5 0 0 1 .5.5v3h3a.5.5 0 0 1 0 1h-3v3a.5.5 0 0 1-1 0v-3h-3a.5.5 0 0 1 0-1h3v-3A.5.5 0 0 1 8 4z"/>' +
                    '    </svg>' +
                    '  </button>' +
                    '  <button type="button" class="btn btn-primary btn-sm task-comment-btn border border-white" onclick="listComments(' + opportunity_id + ', \'' + opportunity_name + '\')">' +
                    '    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-left-text" viewBox="0 0 16 16">' +
                    '      <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1h12zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2H2z"/>' +
                    '      <path d="M3 3.5a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9a.5.5 0 0 1-.5-.5zM3 6a.5.5 0 0 1 .5-.5h9a.5.5 0 0 1 0 1h-9A.5.5 0 0 1 3 6zm0 2.5a.5.5 0 0 1 .5-.5h5a.5.5 0 0 1 0 1h-5a.5.5 0 0 1-.5-.5z"/>' +
                    '    </svg>' +
                    '  </button>' +
                    '  <button type="button" class="btn btn-primary btn-sm task-comment-btn border border-white" onclick="showCreateCommentModal(' + opportunity_id + ', \'' + opportunity_name + '\')">' +
                    '    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-chat-right-quote" viewBox="0 0 16 16">' +
                    '      <path d="M2 1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h9.586a2 2 0 0 1 1.414.586l2 2V2a1 1 0 0 0-1-1H2zm12-1a2 2 0 0 1 2 2v12.793a.5.5 0 0 1-.854.353l-2.853-2.853a1 1 0 0 0-.707-.293H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h12z"/>' +
                    '      <path d="M7.066 4.76A1.665 1.665 0 0 0 4 5.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 1 0 .6.58c1.486-1.54 1.293-3.214.682-4.112zm4 0A1.665 1.665 0 0 0 8 5.668a1.667 1.667 0 0 0 2.561 1.406c-.131.389-.375.804-.777 1.22a.417.417 0 1 0 .6.58c1.486-1.54 1.293-3.214.682-4.112z"/>' +
                    '    </svg>' +
                    '  </button>' +
                    '</div>';
    return icons;
}
