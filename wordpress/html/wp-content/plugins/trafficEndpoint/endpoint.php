<?php
/*
  Plugin Name: Car Detection WebHook Endpoint
  Plugin URI:
  Description: Set up WebHook endpoint to be requested regularly for a limited specific purpose.
  Version: 1.0.0
  Author: Kiho Katsukawa
  Author URI: https://github.com/Keyhole-Koro
 */

$file_path = __DIR__ . '/api_keys.txt';

$api_keys_str = file_get_contents($file_path);

if ($api_keys_str === false) {
    error_log('Failed to read API keys file');
    return;
}

$api_keys_array = explode(',', $api_keys_str);

function is_api_key_valid($api_key) {
    global $api_keys_array;
    return in_array($api_key, $api_keys_array);
}

$body_result_html = "";
$admin_body_result_html = "";

function custom_rest_endpoint_init() {
    register_rest_route('trafficinfo/v1', '/update', array(
        'methods' => 'POST',
        'callback' => 'handle_webhook_request',
        'permission_callback' => '__return_true',
    ));
}
add_action('rest_api_init', 'custom_rest_endpoint_init');

function handle_webhook_request(WP_REST_Request $request) {
    // Check if this is an HTTPS request
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
            'message' => 'Invalid API key',
        ), 403);
    }

    // Get the raw POST data
    $data = $request->get_json_params();

    if (!$data) {
        return new WP_REST_Response(array(
            'status' => 'error',
            'message' => 'No data received',
        ), 400);
    }

    // Proceed with data processing
    if (isset($data['result']) && isset($data['timestamp']) && isset($data['images']) && isset($data['annotated_images'])) {
        // Sanitize and update options
        $body_result = sanitize_text_field($data['result']);
        $timestamp = sanitize_text_field($data['timestamp']);
        $images = $data['images'];
        $annotated_images = $data['annotated_images'];
        
        // Store image data and remove old images
        $upload_dir = wp_upload_dir()['path'];
        $image_links = [];
        foreach (glob("$upload_dir/image_*.jpg") as $old_image) {
            unlink($old_image); // Delete old image
        }
        foreach ($images as $index => $image) {
            $image_data = base64_decode($image);
            $image_filename = "image_{$index}_" . time() . '.jpg';
            $image_path = "$upload_dir/$image_filename";
            file_put_contents($image_path, $image_data);
            $image_links[] = wp_upload_dir()['url'] . "/$image_filename";
        }

        // Store annotated images
        $annotated_image_links = [];
        foreach ($annotated_images as $index => $annotated_image) {
            $annotated_data = base64_decode($annotated_image);
            $annotated_filename = "annotated_image_{$index}_" . time() . '.jpg';
            $annotated_path = "$upload_dir/$annotated_filename";
            file_put_contents($annotated_path, $annotated_data);
            $annotated_image_links[] = wp_upload_dir()['url'] . "/$annotated_filename";
        }

        // Update options
        update_option('body_result_option', $body_result);
        update_option('body_timestamp_option', $timestamp);
        update_option('body_last_updated_option', current_time('timestamp'));
        update_option('body_image_links_option', $image_links);
        update_option('body_annotated_image_links_option', $annotated_image_links);

        // Update HTML outputs
        global $body_result_html, $admin_body_result_html;
        $body_result_html = get_display_body_result('body_image_links_option');
        $admin_body_result_html = get_display_body_result('body_annotated_image_links_option');
    } else {
        return new WP_REST_Response(array(
            'status' => 'error',
            'message' => 'Missing required fields',
        ), 400);
    }

    // Respond with a JSON response (success)
    return new WP_REST_Response(array(
        'status' => 'success',
        'body_result' => get_option('body_result_option', '0'),
        'timestamp' => get_option('body_timestamp_option', 'N/A'),
    ), 200);
}

function get_display_body_result($option_name) {
    $option_value = get_option($option_name, []);

    ob_start();

    echo '<div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);">';
    echo '<h2 style="font-size: 24px; margin-bottom: 10px;">The current number of waiting trucks: ' . esc_html(get_option('body_result_option', '0')) . '</h2>';
    echo '<p style="font-size: 18px; color: #666;">Last updated: ' . date('Y-m-d H:i:s', get_option('body_last_updated_option', 0)) . '</p>';
    
    if ($option_name === 'body_image_links_option') {
        echo '<h3>Detected Images:</h3>';
    } elseif ($option_name === 'body_annotated_image_links_option') {
        echo '<h3>Annotated Images:</h3>';
    }

    foreach ($option_value as $link) {
        echo '<img src="' . esc_url($link) . '" style="max-width: 100%; height: auto; margin-bottom: 10px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);" />';
    }
    echo '</div>';

    $output = ob_get_clean();

    return $output;
}

// PHP code remains unchanged as previously provided
add_action('wp_ajax_update_traffic_info', 'get_traffic_info_html');
add_action('wp_ajax_nopriv_update_traffic_info', 'get_traffic_info_html');

function get_traffic_info_html() {
    global $body_result_html;
    if (empty($body_result_html)) {
        $body_result_html = get_display_body_result('body_image_links_option');
    }
    echo $body_result_html;
    wp_die();
}

add_action('wp_ajax_admin_update_traffic_info', 'get_admin_traffic_info_html');
add_action('wp_ajax_nopriv_admin_update_traffic_info', 'get_admin_traffic_info_html');

function get_admin_traffic_info_html() {
    global $admin_body_result_html;
    if (empty($admin_body_result_html)) {
        $admin_body_result_html = get_display_body_result('body_annotated_image_links_option');
    }
    echo $admin_body_result_html;
    wp_die();
}

function enqueue_custom_scripts() {
    wp_enqueue_script('updateTraffic', plugin_dir_url(__FILE__) . 'js/updateTraffic.js', array('jquery'), null, true);
    wp_localize_script('updateTraffic', 'ajaxurl', array('ajaxurl' => admin_url('admin-ajax.php')));
}
add_action('wp_enqueue_scripts', 'enqueue_custom_scripts');
?>
