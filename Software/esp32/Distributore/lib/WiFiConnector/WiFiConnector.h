// WiFiConnector.h
#ifndef WIFICONNECTOR_H
#define WIFICONNECTOR_H

#include <WiFi.h>
#include <WiFiManager.h>
#include "seriale.h"
#include "lcd_functions.h"

class WiFiConnector {
public:
    WiFiConnector(const char* apName);
    void begin();
    void checkConnection();
    
private:
    WiFiManager wifiManager;
    const char* apName;
};

#endif // WIFICONNECTOR_H
