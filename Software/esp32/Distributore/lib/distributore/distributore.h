#ifndef DISTRIBUTORE_H
#define DISTRIBUTORE_H

// Arduino Basics
#include <Arduino.h>
#include "CONFIG.h"
#include "structs.h"
#include "seriale.h"

// Display LCD
#include "lcd_functions.h"

// RFID
#include "rfid_functions.h"

// WIFI
#include "WiFiConnector.h"

// SERVER WEB
#include "query_functions.h"


// Slot del Prodotto selezionato di Default
#define DEFAULT_PRODUCT 0

// Quantita del Prodotto Default
#define QUANTITA_MINIMA 1


////////// Monitor LCD
// Inizializzazione display LCD
LiquidCrystal_I2C lcd(I2C_ADDR, totalRows, totalColumns);


////////// RFID
// Inizializzazione RFID
MFRC522 rfid(CS, RST);


////////// WI-FI
WiFiConnector wifiConnector(ESP32_AP_NAME);


////////// X MAS
//// Dichiarazione Stati
// Stati della macchina a stati
enum State {
    ATTESA_CHIAVETTA,
    AUTENTICAZIONE_CHIAVETTA,
    MENU,
    RICHIESTA_PRODOTTI,
    SELEZIONE_PRODOTTO,
    SELEZIONE_QUANTITA,
    CHECK_PRODOTTO,
    EROGAZIONE,
    RICHIESTA_SALDO,
    MODIFICA_SALDO,
    AGGIORNA_SALDO,
    MENU_TRANSAZIONI,
    RICHIESTA_ACQUISTI,
    MOSTRA_ACQUISTI,
    VERIFICA_PRODOTTO,
    RICHIESTA_RICARICHE,
    MOSTRA_RICARICHE,
    RIPETI_RICARICA,
    ERROR,
    RESET
};
State current_state = RESET, next_state = ATTESA_CHIAVETTA;
bool state_change = false;


////////// Inizializzazione Distributore
// Varibili
int selected_product = DEFAULT_PRODUCT;
int dot_count;
bool clear_dots = false;
int selected_option;
float delta_saldo;
int selected_type;
float saldo, new_saldo;
int selected_quantity;
int selected_transazione;
bool lcd_error;
int slot;
float importo_transazione;

String ID_Chiavetta;
String nome_prodotto;
JsonDocument user;

// Erogazione
unsigned long intervalMillis, endMillis;
bool printEqualSigns = true;
int currentColumn = 0;

// Opzioni del Menu
String menu_options[3] = {"Distributore", "Saldo", "Transazioni"};
String menu_Transazioni_options[2] = {"Acquisti", "Ricariche"};

//// INPUTS
// Pulsanti
bool PIU, MENO, RETURN, CONFIRM;
bool PIU_old, MENO_old, RETURN_old, CONFIRM_old;
// LM35
int LM35;

//// OUTPUTS
// Leds
bool LED_RGB_R;
bool LED_RGB_G;
bool LED_RGB_B;
// Relè
bool OUT_RELE;

// Errore SQL
bool sqlError;

#endif