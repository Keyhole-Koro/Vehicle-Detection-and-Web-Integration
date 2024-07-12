jQuery(document).ready(function($) {
    function checkWebhookActivity() {
        $.ajax({
            url: ajaxurl.ajaxurl,
            type: 'POST',
            data: {
                action: 'check_webhook_activity'
            },
            success: function(response) {
                console.log('Webhook activity checked:', response);
            },
            error: function(xhr, status, error) {
                console.error('Error checking webhook activity:', error);
            }
        });
    }
    
    // Initial check
    checkWebhookActivity();

    // Check every 5 minutes (300000 milliseconds)
    //setInterval(checkWebhookActivity, 300000); // Adjust the interval as needed
});
