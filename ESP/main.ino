#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Motor functions
#include "motor.h"
//Ultrasonic functions
#include "ultra.h"


// ============================================================
// WIFI
// ============================================================

const char* ssid = "Airtel_SDK_Home";
const char* password = "Home@1482";


// ============================================================
// MQTT
// ============================================================

const char* mqtt_server = "broker.mqtt-dashboard.com";
const char* mqtt_topic = "psna/robo/app";

WiFiClient espClient;
PubSubClient client(espClient);


// ============================================================
// WIFI SETUP
// ============================================================

void setup_wifi() {

  delay(10);

  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);

  WiFi.begin(
    ssid,
    password
  );

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");
  }

  Serial.println();

  Serial.println("WiFi connected");

  Serial.print("IP address: ");

  Serial.println(
    WiFi.localIP()
  );
}


// ============================================================
// MQTT CALLBACK
// ============================================================

void callback(
  char* topic,
  byte* payload,
  unsigned int length
) {

  Serial.print("Message arrived [");

  Serial.print(topic);

  Serial.print("] ");

  
  // ----------------------------------------------------------
  // Convert MQTT payload to String
  // ----------------------------------------------------------

  String message = "";

  for (unsigned int i = 0; i < length; i++) {

    message += (char)payload[i];
  }

  Serial.println(message);


  // ==========================================================
  // PARSE JSON
  // ==========================================================

  DynamicJsonDocument doc(256);

  DeserializationError error =
    deserializeJson(
      doc,
      message
    );


  // ----------------------------------------------------------
  // Check JSON error
  // ----------------------------------------------------------

  if (error) {

    Serial.print("JSON parsing failed: ");

    Serial.println(
      error.c_str()
    );

    return;
  }


  // ==========================================================
  // GET JSON VALUES
  // ==========================================================

  const char* device =
    doc["device"];

  const char* command =
    doc["command"];


  // ----------------------------------------------------------
  // Check values
  // ----------------------------------------------------------

  if (device == nullptr || command == nullptr) {

    Serial.println("Invalid JSON data");

    return;
  }


  Serial.print("Device: ");

  Serial.println(device);

  Serial.print("Command: ");

  Serial.println(command);


  // ==========================================================
  // CHECK DEVICE
  // ==========================================================

  if (strcmp(device, "robo1") != 0) {

    Serial.println("Unknown device");

    return;
  }


  // ==========================================================
  // MOTOR COMMANDS
  // ==========================================================

  if (strcmp(command, "forward") == 0) {

    Serial.println("Motor: FORWARD");

    forward();
  }


  else if (strcmp(command, "reverse") == 0) {

    Serial.println("Motor: REVERSE");

    reverse();
  }


  else if (strcmp(command, "left") == 0) {

    Serial.println("Motor: LEFT");

    left();
  }


  else if (strcmp(command, "right") == 0) {

    Serial.println("Motor: RIGHT");

    right();
  }


  else if (strcmp(command, "stop") == 0) {

    Serial.println("Motor: STOP");

    stop();
  }


  else {

    Serial.println("Unknown motor command");
  }
}


// ============================================================
// MQTT RECONNECT
// ============================================================

void reconnect() {

  while (!client.connected()) {

    Serial.print(
      "Attempting MQTT connection..."
    );


    String clientId =
      "ESP8266Robot-";

    clientId +=
      String(
        random(0xffff),
        HEX
      );


    if (
      client.connect(
        clientId.c_str()
      )
    ) {

      Serial.println("connected");


      client.subscribe(
        mqtt_topic
      );


      Serial.print(
        "Subscribed to: "
      );

      Serial.println(
        mqtt_topic
      );
    }


    else {

      Serial.print(
        "failed, rc="
      );

      Serial.print(
        client.state()
      );

      Serial.println(
        " try again in 5 seconds"
      );

      delay(5000);
    }
  }
}


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(115200);


  // ----------------------------------------------------------
  // Motor initialization
  // ----------------------------------------------------------

  motor_init();
  ultra_init();


  // ----------------------------------------------------------
  // WiFi
  // ----------------------------------------------------------

  setup_wifi();


  // ----------------------------------------------------------
  // MQTT
  // ----------------------------------------------------------

  client.setServer(
    mqtt_server,
    1883
  );

  client.setCallback(
    callback
  );
}


// ============================================================
// LOOP
// ============================================================

void loop() {

  if (!client.connected()) {

    reconnect();
  }

  client.loop();
  float d = dist();


  if (d < 15) {

    Serial.println("OBSTACLE!");
    Serial.print("Distance: ");
    Serial.print(d);
    Serial.println(" cm");
    stop();
  }
}