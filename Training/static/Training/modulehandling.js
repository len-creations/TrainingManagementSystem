document.addEventListener('DOMContentLoaded', function() {
    const submitButton = document.getElementById('submit-button');
    const traineeId = document.getElementById('trainee_id').value;
    const trainingModuleId = document.getElementById('training_module_id').value;

    const messageDiv = document.createElement('div');
    messageDiv.className = 'alert';
    messageDiv.style.display = 'none'; 
    document.body.appendChild(messageDiv); 

    messageDiv.textContent = '';

    // Check if trainee ID and training module ID are present
    if (!traineeId || !trainingModuleId) {
        messageDiv.textContent = 'Kindly register as a trainee.';
        messageDiv.className = 'alert alert-warning'; // Bootstrap warning alert
        messageDiv.style.display = 'block'; // Show the message
        return;
    }
    
    // Fetch the initial status when the page loads
    function fetchTraineeStatus() {
        fetch(`/get-trainee-status/?trainee_id=${traineeId}`) // Adjust the endpoint to match your backend
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Update button text based on some criteria (you can modify this logic)
                    submitButton.textContent = 'Trainee Status Fetched'; // Adjust this as needed
                    messageDiv.style.display = 'none'; // Hide the message
                } else {
                    messageDiv.textContent = 'Kindly register as a trainee.';
                    messageDiv.className = 'alert alert-warning'; // Show the message
                    messageDiv.style.display = 'block'; // Ensure the message is displayed
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while fetching trainee status.');
            });
    }

    // Fetch the initial status when the page loads
    fetchTraineeStatus();

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

document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;
    var contentDiv = document.getElementById('password-reset-content');
    
    // Hide all content initially
    contentDiv.querySelectorAll('h2, p, form').forEach(function(el) {
      el.style.display = 'none';
    });

    // Show content based on the URL path
    if (path.includes('password_reset')) {
      contentDiv.querySelector('form').style.display = 'block';
    } else if (path.includes('password_reset/done')) {
      contentDiv.querySelector('p').style.display = 'block';
    } else if (path.includes('password_reset/complete')) {
      contentDiv.querySelector('p').style.display = 'block';
    } else if (path.includes('password_reset')) {
      contentDiv.querySelector('form').style.display = 'block';
    } else {
      contentDiv.querySelector('h2').textContent = 'Page not found';
      contentDiv.querySelector('p').textContent = 'The page you are looking for does not exist.';
      contentDiv.querySelector('h2').style.display = 'block';
      contentDiv.querySelector('p').style.display = 'block';
    }
  });
  document.addEventListener('DOMContentLoaded', function() {
    const dropdownButton = document.querySelector('.dropbtn');
    const dropdownContent = document.querySelector('.dropdown-content');

    dropdownButton.addEventListener('click', function() {
        // Toggle visibility of dropdown content
        if (dropdownContent.style.display === 'block') {
            dropdownContent.style.display = 'none';
        } else {
            dropdownContent.style.display = 'block';
        }
    });

    // Hide the dropdown when clicking outside of it
    window.addEventListener('click', function(event) {
        if (!event.target.matches('.dropbtn')) {
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            }
        }
    });
});

