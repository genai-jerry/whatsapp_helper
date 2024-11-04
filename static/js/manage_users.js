function showToast(title, message, type = 'success') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <strong>${title}</strong>: ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

class UserManager {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Role removal
        // Handle role removal
        document.querySelectorAll('.selected-roles').forEach(element => {
            element.addEventListener('click', (e) => {
                this.handleRoleRemoval(e);
                e.stopPropagation(); // Prevent event bubbling
            });
        });

        // Role addition
        document.querySelectorAll('.add-role-select').forEach(element => {
            element.addEventListener('change', (e) => {
                this.handleRoleAddition(e);
            });
        });

        // Status toggle
        document.querySelectorAll('.status-toggle').forEach(element => {
            element.addEventListener('change', (e) => {
                this.handleStatusToggle(e);
            });
        });
    
        // Add click handler for reset password button
        document.querySelectorAll('.reset-password-btn').forEach(button => {
            button.addEventListener('click', function(event) {
                const userId = this.getAttribute('data-user-id');
                const userName = this.getAttribute('data-user-name');
                $('#user_id').val(userId);
                $('#user_name').text(userName);
            });
        });
    }

    async handleRoleAddition(event) {
        const select = event.target;
        const selectedOption = select.options[select.selectedIndex];
        const userId = select.dataset.userId;
        const roleId = select.value;
        const roleName = selectedOption.dataset.roleName;

        if (!roleId) return; // Skip if "Add role..." is selected

        try {
            const response = await fetch('/user/role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'add', user_id: userId, role_id: roleId })
            });

            if (!response.ok) {
                throw new Error('Failed to add role');
            }

            // Create and add new badge
            const badgeContainer = select.closest('td').querySelector('.selected-roles');
            const newBadge = document.createElement('span');
            newBadge.className = 'badge bg-primary me-1 mb-1 role-badge';
            newBadge.dataset.roleName = roleName;
            newBadge.innerHTML = `
                <span class="role-name">${roleName}</span>
                <i class="bi bi-x-circle-fill remove-role" 
                   data-user-id="${userId}" 
                   data-role-id="${roleId}"></i>
            `;
            badgeContainer.appendChild(newBadge);

            // Remove option from dropdown
            selectedOption.remove();

            // Reset select to placeholder
            select.value = '';

            showToast('Success', `Role "${roleName}" added successfully`);
        } catch (error) {
            console.error('Error adding role:', error);
            showToast('Error', 'Failed to add role', 'error');
            select.value = ''; // Reset select on error
        }
    }

    async handleRoleRemoval(event) {
        event.preventDefault();
        event.stopPropagation();

        const badge = event.target.closest('.role-badge');
        const removeIcon = badge.querySelector('.remove-role');
        const userId = removeIcon.dataset.userId;
        const roleId = removeIcon.dataset.roleId;
        const roleName = badge.dataset.roleName;

        if (!confirm(`Are you sure you want to remove the role "${roleName}"?`)) {
            return;
        }

        try {
            const response = await fetch('/user/role', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'remove', user_id: userId, role_id: roleId })
            });

            if (!response.ok) {
                throw new Error('Failed to remove role');
            }

            // Add role back to dropdown
            const select = badge.closest('td').querySelector('.add-role-select');
            const option = new Option(roleName, roleId);
            option.dataset.roleName = roleName;
            select.add(option);

            // Remove the badge
            badge.remove();

            showToast('Success', `Role "${roleName}" removed successfully`);
        } catch (error) {
            console.error('Error removing role:', error);
            showToast('Error', 'Failed to remove role', 'error');
        }
    }

    async handleStatusToggle(event) {
        const toggle = event.target;
        const userId = toggle.dataset.userId;
        const isActive = toggle.checked;
        const statusLabel = toggle.nextElementSibling;
        const originalState = !isActive; // Store original state in case we need to revert

        try {
            const response = await fetch('/user/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    user_id: userId, 
                    active: isActive 
                })
            });

            if (!response.ok) {
                throw new Error('Failed to update status');
            }

            // Update the label text
            statusLabel.textContent = isActive ? 'Active' : 'Inactive';

            // Update row styling
            const userRow = toggle.closest('tr');
            if (isActive) {
                toggle.checked = true;
                userRow.classList.remove('table-secondary');
            } else {
                toggle.checked = false;
                userRow.classList.add('table-secondary');
            }

            showToast('Success', `User ${isActive ? 'activated' : 'deactivated'} successfully`);
        } catch (error) {
            console.error('Error updating status:', error);
            // Revert the toggle state
            toggle.checked = originalState;
            statusLabel.textContent = originalState ? 'Active' : 'Inactive';
            showToast('Error', 'Failed to update user status', 'error');
        }
    }

    async checkPasswordMatch() {
        const newPassword = $('#new_password');
        const confirmPassword = $('#confirm_password');
        const feedback = $('#password-feedback');
        
        if (newPassword.val() !== confirmPassword.val()) {
            newPassword.addClass('is-invalid');
            confirmPassword.addClass('is-invalid');
            feedback.text('Passwords do not match').addClass('invalid-feedback').show();
            return false;
        }
        
        try {
            newPassword.removeClass('is-invalid').addClass('is-valid');
            confirmPassword.removeClass('is-invalid').addClass('is-valid');
            feedback.text('').hide();
            const userId = $('#user_id').val();
            const response = await fetch('/user/password', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id: userId, new_password: newPassword.val() })
            });

            if (!response.ok) {
                throw new Error('Failed to check password match');
            }
            // close modal
            $('#resetPasswordModal').modal('hide');
            showToast('Success', 'Password reset successfully');
            // clear form
            newPassword.val('');
            confirmPassword.val('');
        } catch (error) {
            console.error('Error checking password match:', error); 
            return false;
        }
        
        return true;
    }
    
}

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.userManager = new UserManager();
});

