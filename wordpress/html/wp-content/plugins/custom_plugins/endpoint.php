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

// Handle WebHook request to update options
function handle_webhook_request() {
    // Check if this is a POST request
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {

        // Get the API key from the request headers
        $api_key = isset($_SERVER['HTTP_X_API_KEY']) ? $_SERVER['HTTP_X_API_KEY'] : '';

        // Check if the API key and IP address are valid
        if (!is_api_key_valid($api_key)) {
            // Respond with a JSON response (access denied)
            header('Content-Type: application/json');
            echo json_encode(array(
                'status' => 'error',
                'message' => 'Invalid API key or IP address'
            ));
            exit;
        }

        // Get the raw POST data
        $post_body = file_get_contents('php://input');
        $data = json_decode($post_body, true);

        // Check if the 'result' and 'timestamp' keys exist in the body
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

        // Respond with a JSON response (success)
        header('Content-Type: application/json');
        echo json_encode(array(
            'status' => 'success',
            'body_result' => get_option('body_result_option', '0'),
            'timestamp' => get_option('body_timestamp_option', 'N/A')
        ));
        exit;
    }
}
add_action('init', 'handle_webhook_request');

// Display the updated result, timestamp, and age check at the top of the homepage
function display_body_result() {
    $body_result = get_option('body_result_option', '0');
    $timestamp = get_option('body_timestamp_option', 'N/A');
    $last_updated = get_option('body_last_updated_option', 0);
    $current_time = current_time('timestamp');
    $time_diff = $current_time - $last_updated;

    echo '<div style="background-color: #f0f0f0; padding: 10px; text-align: center;">';
    echo '<h2>Updated Body Result: ' . esc_html($body_result) . '</h2>';
    echo '<h3>Timestamp: ' . esc_html($timestamp) . '</h3>';

    if ($time_diff > 10) {
        echo '<h3 style="color: red;">The information might be old</h3>';
    }

    echo '</div>';
}
add_action('wp_head', 'display_body_result');
?>
