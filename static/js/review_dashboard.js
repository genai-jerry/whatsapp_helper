const collapsibleSections = document.querySelectorAll('.collapse');

collapsibleSections.forEach(section => {
    const minusIcon = section.previousElementSibling.querySelector('.bi-dash');
    const plusIcon = section.previousElementSibling.querySelector('.bi-plus');
    
    section.addEventListener('show.bs.collapse', function () {
        minusIcon.classList.remove('d-none');
        plusIcon.classList.add('d-none');
    });
    
    section.addEventListener('hide.bs.collapse', function () {
        minusIcon.classList.add('d-none');
        plusIcon.classList.remove('d-none');
    });
});

// Add event listener for employee dropdown
const employeeSelect = document.getElementById('employeeSelect');

employeeSelect.addEventListener('change', function() {
    const selectedUserId = this.value;
    if (selectedUserId) {
        window.location.href = `/review/${destination}/${selectedUserId}`;
    }
});