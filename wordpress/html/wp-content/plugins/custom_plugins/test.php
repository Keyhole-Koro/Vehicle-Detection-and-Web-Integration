<?php
/*
  Plugin Name: test
  Plugin URI:
  Description: 
  Version: 1.0.0
  Author: Kiho Katsukawa
  Author URI: https://github.com/Keyhole-Koro
 */

 // Register a simple shortcode to test
function test_shortcode() {
    return "Shortcode is working!";
}
add_shortcode('test_shortcode', 'test_shortcode');

?>