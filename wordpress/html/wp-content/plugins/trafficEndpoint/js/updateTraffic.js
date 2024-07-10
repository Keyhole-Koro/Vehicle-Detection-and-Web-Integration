jQuery(document).ready(function($) {
    function updateTrafficInfo(action, targetClass) {
        $.ajax({
            url: ajaxurl.ajaxurl,
            type: 'POST',
            data: {
                action: action
            },
            success: function(response) {
                $(targetClass).html(response);
            }
        });
    }

    // Update regular traffic info
    function updateRegularTrafficInfo() {
        updateTrafficInfo('update_traffic_info', '.traffic-info');
    }

    // Update admin traffic info
    function updateAdminTrafficInfo() {
        updateTrafficInfo('admin_update_traffic_info', '.admin-traffic-info');
    }

    // Initial update
    updateRegularTrafficInfo();
    updateAdminTrafficInfo();

    // Set interval for regular traffic info update
    setInterval(updateRegularTrafficInfo, 60000);

    // Set interval for admin traffic info update
    setInterval(updateAdminTrafficInfo, 60000);
});
