// WiFiConnector.cpp
#include "WiFiConnector.h"

WiFiConnector::WiFiConnector(const char* apName) : apName(apName) {}

void WiFiConnector::begin() {
    lcdWrite("  Wi-Fi Setup   ", "AP -> " + String(ESP32_AP_NAME));
    printToTerminal("Configura il Wi-Fi connettendoti a " + String(ESP32_AP_NAME));
    if (!wifiManager.autoConnect(apName)) {
        printToTerminal("Failed to connect and hit timeout");
        ESP.restart();
    }

    printToTerminal("Connected successfully!");
    lcdWrite("     Wi-Fi      ", "   Connected    ", 1000);
}

void WiFiConnector::checkConnection() {
    if (WiFi.status() != WL_CONNECTED) {
        printToTerminal("WiFi connection lost, restarting WiFiManager...");
        lcdWrite("Connection lost ", "AP -> " + String(ESP32_AP_NAME));
        wifiManager.startConfigPortal(apName);
        printToTerminal("Configuration completed, restarting...");
        lcdWrite("     Wi-Fi      ", "  Reconnected   ");
        delay(1000);
        ESP.restart();
    }
}
