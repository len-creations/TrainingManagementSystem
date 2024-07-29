document.addEventListener('DOMContentLoaded', function() {
    // Define the button and hidden inputs
    const markCompleteBtn = document.getElementById('mark-complete-btn');
    const moduleId = document.getElementById('module-id').value;
    const traineeId = document.getElementById('trainee-id').value;

    console.log('module_id', moduleId);
    console.log('trainee_id', traineeId);

    // Function to update the module completion status
    function updateModuleStatus(isCompleted) {
        fetch(/update-module-status/,{
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: new URLSearchParams({
                'module_id': moduleId,
                'trainee_id': traineeId,
                'completed': isCompleted,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (isCompleted) {
                markCompleteBtn.textContent = 'Mark Module as Incomplete';
            } else {
                markCompleteBtn.textContent = 'Mark Module as Completed';
            }
        })
        .catch(error => {
            console.error('Error updating module status:', error);
        });
    }

    // Initialize button text based on the current state
    const isCompleted = markCompleteBtn.dataset.completed === '1';
    markCompleteBtn.textContent = isCompleted ? 'Mark Module as Incomplete' : 'Mark Module as Completed';

    // Event handler for button click
    markCompleteBtn.addEventListener('click', function() {
        const currentStatus = markCompleteBtn.textContent.includes('Completed');
        updateModuleStatus(!currentStatus);
        // Update the button data attribute for future reference
        markCompleteBtn.dataset.completed = !currentStatus ? '1' : '0';
    });
});