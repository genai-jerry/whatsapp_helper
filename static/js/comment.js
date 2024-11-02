// Function to list all comments for a given opportunity
function listComments(opportunity_id, opportunity_name) {
    const tableBody = document.getElementById('commentListTableBody');
    if (!tableBody) {
        console.error('Comment list table body not found');
        return;
    }
    
    tableBody.innerHTML = ''; // Clear existing rows

    // Fetch comment data from the server
    fetch(`/comment?opportunity_id=${opportunity_id}`)
        .then(response => response.json())
        .then(data => {
            data.comments.forEach(comment => {
                const createdDate = new Date(comment.created_at);
                const formattedCreatedDate = createdDate.toLocaleString('en-GB', {
                    day: '2-digit',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                });
                
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${opportunity_name}</td>
                    <td>${comment.content}</td>
                    <td>${comment.creator_name}</td>
                    <td>${formattedCreatedDate}</td>
                `;
                tableBody.appendChild(row);
            });
            
            // Show the modal after populating the table
            const commentListModal = new bootstrap.Modal(document.getElementById('commentListModal'));
            commentListModal.show();
        })
        .catch(error => console.error('Error fetching comments:', error));
}

// Function to show the create comment modal
function showCreateCommentModal(opportunity_id, opportunity_name) {
    const createCommentModal = new bootstrap.Modal(document.getElementById('createCommentModal'));
    document.getElementById('commentOpportunityId').value = opportunity_id;
    document.getElementById('commentOpportunityName').value = opportunity_name;
    createCommentModal.show();
}

// Function to create a new comment
function createComment(event) {
    event.preventDefault();
    const form = document.getElementById('createCommentForm');
    const formData = new FormData(form);
    const commentFeedback = document.getElementById('commentFeedback');

    fetch('/comment', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        commentFeedback.classList.remove('alert-danger');
        commentFeedback.classList.add('alert-success');
        commentFeedback.textContent = data.message;
        commentFeedback.style.display = 'block';
        
        setTimeout(() => {
            commentFeedback.style.display = 'none';
            const createCommentModal = bootstrap.Modal.getInstance(document.getElementById('createCommentModal'));
            createCommentModal.hide();
            listComments(document.getElementById('commentOpportunityId').value, 
                document.getElementById('commentOpportunityName').value);
            form.reset();
        }, 1500);
        
        commentFeedback.style.display = 'block';
        setTimeout(() => {
            commentFeedback.style.display = 'none';
            form.reset();
        }, 3000);
    })
    .catch(error => {
        console.error('Error creating comment:', error);
        commentFeedback.classList.remove('alert-success');
        commentFeedback.classList.add('alert-danger');
        commentFeedback.textContent = 'Error creating comment. Please try again.';
        commentFeedback.style.display = 'block';
    });
}

// Ensure the DOM is fully loaded before attaching event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for the button that opens the comment list modal
    const openListModalBtn = document.querySelector('[data-bs-target="#commentListModal"]');
    if (openListModalBtn) {
        openListModalBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const opportunityId = this.getAttribute('data-opportunity-id');
            listComments(opportunityId);
        });
    }

    // Add event listener for the button that opens the create comment modal
    const openCreateModalBtn = document.querySelector('[data-bs-target="#createCommentModal"]');
    if (openCreateModalBtn) {
        openCreateModalBtn.addEventListener('click', function(event) {
            event.preventDefault();
            const opportunityId = this.getAttribute('data-opportunity-id');
            const opportunityName = this.getAttribute('data-opportunity-name');
            showCreateCommentModal(opportunityId, opportunityName);
        });
    }

    const createCommentForm = document.getElementById('createCommentForm');
    if (createCommentForm) {
        createCommentForm.addEventListener('submit', createComment);
    }
});

function loadComments(opportunityId, page = 1) {
    fetch(`/comment/?opportunity_id=${opportunityId}&page=${page}`)
        .then(response => response.json())
        .then(data => {
            // Update the comments list in the DOM
            updateCommentsList(data.comments);
            // Update pagination if necessary
            updatePagination(data.page, data.total_comments, data.per_page);
        })
        .catch(error => console.error('Error:', error));
}

function updateCommentsList(comments) {
    const commentsList = document.getElementById('commentsList');
    commentsList.innerHTML = '';
    comments.forEach(comment => {
        const commentElement = document.createElement('div');
        commentElement.className = 'comment';
        commentElement.innerHTML = `
            <p>${comment.content}</p>
            <small>By ${comment.creator_username} on ${new Date(comment.created_at).toLocaleString()}</small>
        `;
        commentsList.appendChild(commentElement);
    });
}

function updatePagination(currentPage, totalComments, perPage) {
    // Implement pagination UI update logic here
}
