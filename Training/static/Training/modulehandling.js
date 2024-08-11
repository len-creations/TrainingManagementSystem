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

