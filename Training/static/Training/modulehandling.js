$(document).ready(function() {
    $('#submit-button').click(function(e) {
        e.preventDefault();
        
        // Get values from form elements
        let progressElement = $('#id_progress');
        let traineeElement = $('#id_trainee');
        let progress = parseInt(progressElement.val(), 10);
        
        if (isNaN(progress)) {
            alert("Progress is not a valid number.");
            return;
        }
        
        // Validate progress value
        if (progress < 100) {
            alert("Progress must be 100 to update modules and exams.");
            return;
        }

        let traineeId = traineeElement.val();
        
        if (!traineeId) {
            alert("Please select a trainee.");
            return;
        }
        
        $.ajax({
            url: "{% url 'trainee_progress' %}",
            method: "POST",
            data: $('#trainee-progress-form').serialize(),
            success: function(response) {
                if (response.status === 'success') {
                    alert(response.message);
                    $('#trainee-progress-form')[0].reset();  // Clear the form
                } else {
                    alert(response.message);
                }
            },
            error: function(xhr, status, error) {
                alert("An error occurred: " + error);
            }
        });
    });
});

