jQuery(document).ready(function($) {
    function updateCustomField() {
        $.ajax({
            url: ajaxurl.ajaxurl,
            type: 'POST',
            data: {
                action: 'update_traffic_info'
            },
            success: function(response) {
                $('.traffic-information').html(response);
            }
        });
    }

    updateCustomField();

    setInterval(updateCustomField, 60000);
});
