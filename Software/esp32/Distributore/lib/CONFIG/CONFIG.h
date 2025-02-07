#ifndef CONFIG_h
#define CONFIG_h

////////// CONFIGUARAZIONE ESP32
// Impostazioni Wi-Fi
#define ESP32_AP_NAME "ESP32_AP"

// Impostazioni del server
#define SERVER_IP "172.20.10.7"
#define SERVER_PORT 8080

// Terminale ON/OFF (Disabilita la possibilità di visualizzare su terminale gli avvenimenti del distributore)
#define TERMINALE true
#define SERIAL_SPEED 115200


//// CONFIGURAZIONE PINS
// PULSANTI
#define PIN_MENO 23
#define PIN_PIU 33
#define PIN_RETURN 25
#define PIN_CONFIRM 32

/// LED
// RGB
#define PIN_LED_RGB_R 15
#define PIN_LED_RGB_G 4
#define PIN_LED_RGB_B 2

// LM35 SENSOR
#define LM35_SENSOR 34

// Monitor LCD
#define I2C_SCL 18
#define I2C_SDA 5
#define I2C_ADDR 0x20
#define totalRows 2
#define totalColumns 16

// RFID
#define SCK 27
#define MOSI 14
#define MISO 12
#define RST 13
#define CS 26

// Relè Erogazione
#define RELE 22

// Ingressi Isolati
#define IN_ISO_1 19
#define IN_ISO_2 21

///////////////////////////////////////////// CONFIGUARAZIONE DISTRIBUTORE

// Aggiornamento del sensore di temperatura in ms
#define SENSOR_INTERVAL 60000

// Durata dell'erogazione dei prodotti in ms
#define TIMER_EROGAZIONE 5000
// Intervallo update schermo durante l'erogazione
#define INTERVAL_EROG TIMER_EROGAZIONE / totalColumns

// Numero limite delle transazioni visualizzate
#define LIMITE_TRANSAZIONI 10

// Numero di Slot Massimi
#define MAX_SLOT 9

#endif