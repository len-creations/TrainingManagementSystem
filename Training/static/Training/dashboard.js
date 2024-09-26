document.addEventListener('DOMContentLoaded', function() {
    const trainingsDataElement = document.getElementById('trainingsData');
    if (!trainingsDataElement) {
        console.error('Element with ID "trainingsData" not found');
        return;
    }

    const trainingsData = JSON.parse(trainingsDataElement.textContent);

    const canvasElement = document.getElementById('trainingsPerTeam');
    if (!canvasElement) {
        console.error('Element with ID "trainingsPerTeam" not found');
        return;
    }

    const ctx = canvasElement.getContext('2d');

    // Extract colors from trainingsData
    const backgroundColors = trainingsData.colors;
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

    // Ensure that each dataset has its own set of colors if needed
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trainingsData.labels,
            datasets: [
                {
                    label: 'Planned Trainings',
                    data: trainingsData.datasets[0].data,
                    backgroundColor: backgroundColors[0], 
                    borderColor: backgroundColors[0],
                    borderWidth: 1
                },
                {
                    label: 'Completed Trainings',
                    data: trainingsData.datasets[1].data,
                    backgroundColor: backgroundColors[1], 
                    borderColor: backgroundColors[1],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Team'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Trainings'
                    },
                    ticks: {
                        stepSize: 1,  // Adjust step size as needed
                        callback: function(value) {
                            return value;  // Custom tick label formatting if needed
                        }
                    }
                }
            }
        }
    });
});