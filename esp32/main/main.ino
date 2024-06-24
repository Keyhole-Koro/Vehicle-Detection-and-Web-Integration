#include "esp_camera.h"
#include "WiFi.h"
#include <esp_http_server.h>
#include <Arduino.h>

#define CAMERA_MODEL_AI_THINKER
#include "camera_pins.h"

httpd_handle_t camera_httpd = NULL;

static esp_err_t capture_handler(httpd_req_t *req){
   camera_fb_t * fb = NULL;
   esp_err_t res = ESP_OK;
   int64_t fr_start = esp_timer_get_time();
   
   fb = esp_camera_fb_get();
   if (!fb) {
       Serial.println("Camera capture failed");
       httpd_resp_send_500(req);
       return ESP_FAIL;
   }
   
   httpd_resp_set_type(req, "image/jpeg");
   size_t fb_len = fb->len;
   res = httpd_resp_send(req, (const char *)fb->buf, fb->len);
   esp_camera_fb_return(fb);
   
   int64_t fr_end = esp_timer_get_time();
   Serial.printf("JPG: %uB %ums\n", (uint32_t)(fb_len), (uint32_t)((fr_end - fr_start)/1000));
   
   return res;
}

void startCameraServer(){
   httpd_config_t config = HTTPD_DEFAULT_CONFIG();
   httpd_uri_t capture_uri = {
       .uri       = "/capture",
       .method    = HTTP_GET,
       .handler   = capture_handler,
       .user_ctx  = NULL
   };

   Serial.printf("Starting web server on port: '%d'\n", config.server_port);
   if (httpd_start(&camera_httpd, &config) == ESP_OK) {
       httpd_register_uri_handler(camera_httpd, &capture_uri);
   }
}

void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  char *ssid;
  char *password;

  ssid = getenv("SSID");
  password = getenv("PASSWORD");

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed");
    return;
  }

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;
  } else {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  Serial.println("Camera initialized");

  startCameraServer();
}

void loop() {
}