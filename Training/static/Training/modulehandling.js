document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById('submit-button');
    const messageDiv = document.getElementById('message');
    const traineeId = document.getElementById('trainee_id').value;
    const trainingModuleId = document.getElementById('training_module_id').value;

    // Check if trainee ID and training module ID are present
    if (!traineeId || !trainingModuleId) {
        alert('Trainee ID or Training Module ID is missing.');
        return;
    }

    // Function to fetch the current status of the module
    function fetchModuleStatus() {
        fetch(`/get-module-status/?trainee_id=${traineeId}&training_module_id=${trainingModuleId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Set button text based on completion status
                    submitButton.textContent = data.progress === 100 ? 'Uncomplete Module' : 'Mark Module Complete';
                } else {
                    console.error(data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching module status.');
            });
    }

    // Fetch the initial status when the page loads
    fetchModuleStatus();

    submitButton.addEventListener('click', function() {
        const action = submitButton.textContent === 'Mark Module Complete' ? 'complete' : 'uncomplete';

        const formData = new URLSearchParams();
        formData.append('trainee_id', traineeId);
        formData.append('training_module_id', trainingModuleId);
        formData.append('completed_modules', '1'); // Example value
        formData.append('action', action); // Add action to the request

        fetch('/update-module-status/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData.toString(),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                messageDiv.textContent = data.message;
                messageDiv.style.display = 'block';
                submitButton.textContent = action === 'complete' ? 'Uncomplete Module' : 'Mark Module Complete';
            } else if (data.status === 'info') {
                messageDiv.textContent = data.message;
                messageDiv.style.display = 'block';
            } else {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
    });
});