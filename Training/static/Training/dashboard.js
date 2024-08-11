document.addEventListener('DOMContentLoaded', function() {
    // Check if the element exists before accessing it
    const trainingsDataElement = document.getElementById('trainingsData');
    if (!trainingsDataElement) {
        console.error('Element with ID "trainingsData" not found');
        return;
    }

    // Retrieve the JSON data from the script tag
    const trainingsData = JSON.parse(trainingsDataElement.textContent);

    const canvasElement = document.getElementById('trainingsPerTeam');
    if (!canvasElement) {
        console.error('Element with ID "trainingsPerTeam" not found');
        return;
    }

    function getRandomColor() {
        const letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // Create a color array if not provided
    const colors = trainingsData.labels.map(() => getRandomColor());

    const ctx = canvasElement.getContext('2d');

    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trainingsData.labels,
            datasets: [{
                label: 'Trainings Taken',
                data: trainingsData.data,
                backgroundColor: colors,  // Apply the colors
                borderColor: colors.map(color => color.replace('0.2', '1')),  // Use a darker shade for borders
                borderWidth: 1
            }]
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
                    }
                }
            }
        }
    });
});