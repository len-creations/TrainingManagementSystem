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