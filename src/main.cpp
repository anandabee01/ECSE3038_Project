#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include "env.h"

#include <cstdlib>
#include <iostream>
#include <string>

#define lightpin 23
#define fanpin 22
#define pir 18

const int oneWireBus = 19;     

// Setup instance of oneWire to communicate with any OneWire devices
OneWire oneWire(oneWireBus);
DallasTemperature sensors(&oneWire);

void setup() 
{
  pinMode(lightpin, OUTPUT);
  pinMode(fanpin, OUTPUT);
  pinMode(pir, INPUT);

  Serial.begin(9600);
  sensors.begin();
  
  WiFi.begin(WIFI_SSID,WIFI_PASS);
  Serial.println("Connecting");

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println(" ");
  Serial.println("Connected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() 
{
  if (WiFi.status() == WL_CONNECTED)
{
    //Post Request
    HTTPClient http;
    http.begin(postrequest);

    http.addHeader("Content-Type", "application/json");
    StaticJsonDocument<1024> doc;
    String httpRequestData;

    sensors.requestTemperatures(); 
    Serial.print("Temp: ");
    Serial.println(sensors.getTempCByIndex(0));

    Serial.print("Distance: ");
    Serial.println(digitalRead(tempsensor));
    doc["presence"] = digitalRead(dis_sensor);
    doc["temp"] = sensors.getTempCByIndex(0);

    serializeJson(doc, httpRequestData);
    // Send HTTP POST request
    int httpResponseCode = http.PUT(httpRequestData);
   String http_response;
    Serial.println("put success");
    if (httpResponseCode>0) 
    {
      Serial.print("HTTP Response code from request: ");
      Serial.println(httpResponseCode);
      Serial.print("HTTP Response from server: ");
      http_response = http.getString();
      Serial.println(http_response);
      Serial.println(" ");
    }
    else                                      //if response is negative
    {
      Serial.print("Error code: ");
      http_response = http.getString();
      Serial.println(httpResponseCode);
    }
    http.end();
      delay(2000);

    //GET Request
    HTTPClient http;

    String http_response;

    http.begin(getrequest);

    int httpResponseCode = http.GET();

    if(httpResponseCode>0){
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);

      Serial.print("Response from server: ");
      http_response = http.getString();
      
    }
    else {
      Serial.print("Error Code: ");
      Serial.println(httpResponseCode);
    }

    http.end();

    StaticJsonDocument<1024> doc;
    DeserializationError error = deserializeJson(doc, http_response);

    if (error) {
      Serial.print("Deserialize Json() failed: ");
      Serial.println(error.c_str());
      return;
    }

    bool light_switch = doc["light"];
    bool fan_switch = doc["fan"];

    Serial.println("data");
    Serial.print("light switch: ");
    Serial.println(light_switch);
    Serial.print("fan switch: ");
    Serial.println(fan_switch);
    Serial.println("");

    digitalWrite(light, light_switch);
    digitalWrite(fan, fan_switch);
  }
  else {
    Serial.println(“WiFi Disconnected”);
  }
}