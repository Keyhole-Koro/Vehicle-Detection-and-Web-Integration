<?php
/*
  Plugin Name: Car Detection WebHook Endpoint
  Plugin URI:
  Description: Set up WebHook endpoint to be requested regularly for a limited specific purpose.
  Version: 1.0.0
  Author: Kiho Katsukawa
  Author URI: https://github.com/Keyhole-Koro
 */

define('VALID_API_KEY', '33f2c126-2711-4690-8e0a-87bd1d8f6386');

function is_api_key_valid($api_key) {
    return $api_key === VALID_API_KEY;
}

function custom_rest_endpoint_init() {
    register_rest_route('trafficinfo/v1', '/update', array(
        'methods' => 'POST',
        'callback' => 'handle_webhook_request',
        'permission_callback' => '__return_true', // We will handle permissions in the callback
    ));
}
add_action('rest_api_init', 'custom_rest_endpoint_init');

function handle_webhook_request(WP_REST_Request $request) {
    // Check if this is a HTTPS request
    if (!isset($_SERVER['HTTPS']) || $_SERVER['HTTPS'] !== 'on') {
        return new WP_REST_Response(array(
            'status' => 'error',
            'message' => 'HTTPS connection is required'
        ), 400);
    }

    // Get the API key from the request headers
    $api_key = $request->get_header('X-API-Key');

    // Check if the API key is valid
    if (!is_api_key_valid($api_key)) {
        return new WP_REST_Response(array(
            'status' => 'error',
            'message' => 'Invalid API key'
        ), 403);
    }

    // Get the raw POST data
    $data = $request->get_json_params();
    
    // Proceed with data processing
    if (isset($data['result']) && isset($data['timestamp'])) {
        // Sanitize and update options
        $body_result = sanitize_text_field($data['result']);
        $timestamp = sanitize_text_field($data['timestamp']);
        update_option('body_result_option', $body_result);
        update_option('body_timestamp_option', $timestamp);
        update_option('body_last_updated_option', current_time('timestamp'));
    } else {
        // If keys are missing, update with default values
        update_option('body_result_option', '0');
        update_option('body_timestamp_option', 'N/A');
        update_option('body_last_updated_option', current_time('timestamp'));
    }

    // Get the updated body result HTML
    $body_result_html = get_display_body_result();

    // Respond with a JSON response (success)
    return new WP_REST_Response(array(
        'status' => 'success',
        'body_result' => get_option('body_result_option', '0'),
        'timestamp' => get_option('body_timestamp_option', 'N/A')
    ), 200);
}

function get_display_body_result() {
    $body_result = get_option('body_result_option', '0');
    $timestamp = get_option('body_timestamp_option', 'N/A');
    $last_updated = get_option('body_last_updated_option', 0);

    ob_start();

    echo '<div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">';
    echo '<h2 style="font-size: 24px; margin-bottom: 10px;">The current number of waiting trucks: ' . esc_html($body_result) . '</h2>';
    echo '<p style="font-size: 18px; color: #666;">Last updated: ' . date('Y-m-d H:i:s', $last_updated) . '</p>';

    echo '</div>';

    $output = ob_get_clean();

    return $output;
}

add_action('wp_ajax_update_traffic_info', 'update_traffic_info');
add_action('wp_ajax_nopriv_update_traffic_info', 'update_traffic_info');

function update_traffic_info() {
    $body_result_html = get_display_body_result();
    echo $body_result_html;
    wp_die();
}

function enqueue_custom_scripts() {
    wp_enqueue_script('updateTraffic', plugin_dir_url(__FILE__) . 'js/updateTraffic.js', array('jquery'), null, true);
    wp_localize_script('updateTraffic', 'ajaxurl', array('ajaxurl' => admin_url('admin-ajax.php')));
}
add_action('wp_enqueue_scripts', 'enqueue_custom_scripts');

?>
