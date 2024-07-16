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


function getOptionColor(selectedValue, options, colorKey) {
    var selectedOption = options.find(function(option) {
        return option.name === selectedValue;
    });
    return selectedOption ? selectedOption[colorKey] : null;
}