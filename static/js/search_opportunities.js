$(document).ready(function() {
    var opportunitySearch = $('#opportunityName');
    var opportunityList = $('#opportunityList');
    var selectedOpportunityId = $('#taskOpportunityId');
    var searchTimeout;
  
    opportunitySearch.on('input', function() {
      clearTimeout(searchTimeout);
      var query = $(this).val();
  
      if (query.length < 2) {
        opportunityList.empty();
        return;
      }
  
      searchTimeout = setTimeout(function() {
        $.ajax({
          url: '/opportunity/search_opportunities',
          method: 'POST',
          contentType: 'application/json',
          data: JSON.stringify({ query: query }),
          success: function(data) {
            opportunityList.empty();
            data.forEach(function(opportunity) {
              var listItem = $('<li>')
                .addClass('list-group-item list-group-item-action')
                .text(opportunity.name + ' (' + opportunity.email + ') - ' + opportunity.phone)
                .data('id', opportunity.id)
                .data('name', opportunity.name);
              opportunityList.append(listItem);
            });
            opportunityList.show(); // Make sure the list is visible
          },
          error: function(xhr, status, error) {
            console.error('Error searching opportunities:', error);
            showFeedback('Error searching opportunities. Please try again.', false);
          }
        });
      }, 300);
    });
  
    opportunityList.on('click', 'li', function() {
      var selected = $(this);
      selectedOpportunityId.val(selected.data('id'));
      opportunitySearch.val(selected.data('name'));
      opportunityList.hide(); // Hide the list after selection
    });
  
    $(document).on('click', function(event) {
      if (!$(event.target).closest('#opportunityList, #opportunityName').length) {
        opportunityList.hide();
      }
    });
  });
